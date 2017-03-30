from django.conf import settings
from .models import Visit, Visitor, User, Cookie
import functools
import string
import random
import base64
import struct
import socket
import logging
log = logging.getLogger(__name__)

#TODO: Fix bug where no visitors_v1 is set when a user visits http://nstoler.com/notepad, receives a
#      301 to https, and retrieves the https url.
#TODO: Grab info about the IP address at the time. Stuff like the ISP, ASN, and geoip data.
#      That stuff can change, especially as IPv4 addresses are bought and sold increasingly.
#      Maybe run a daemon separate from Django to do it in the background, to not hold up the
#      response. Possible data sources:
#      http://ipinfo.io/developers (ASN, geiop)
#      https://stat.ripe.net/docs/data_api (semi-official, but ASN only)

ALPHABET1 = string.ascii_lowercase + string.ascii_uppercase + string.digits + '+-'
COOKIE_MAX_AGE = 10*365*24*60*60  # 10 years


# Decorator.
def add_visit(view):
  """Wrap a view with a function that logs the visit."""
  #TODO: This might be better written as middleware, but I'll have to look into it.
  @functools.wraps(view)
  def wrapped_view(request, *nargs, **kwargs):
    visit = get_or_create_visit_and_visitor(request)
    response = view(request, *nargs, **kwargs)
    return set_cookies(visit, response)
  return wrapped_view


# Decorator.
def add_and_get_visit(view):
  """Wrap a view with a function that logs the visit and provides it as an argument to the view."""
  #TODO: This might be better written as middleware, but I'll have to look into it.
  @functools.wraps(view)
  def wrapped_view(request, *nargs, **kwargs):
    visit = get_or_create_visit_and_visitor(request)
    response = view(request, visit, *nargs, **kwargs)
    return set_cookies(visit, response)
  return wrapped_view


def get_or_create_visit_and_visitor(request):
  """Do the actual work of logging the visit. Return the Visit object."""
  cookies_got = get_cookies(request)
  headers = request.META
  ip = headers.get('REMOTE_ADDR')
  user_agent = headers.get('HTTP_USER_AGENT')
  visitor = get_or_create_visitor(ip, cookies_got, user_agent)
  visit = create_visit(request, visitor)
  return visit


def get_cookies(request):
  cookie1 = request.COOKIES.get('visitors_v1')
  cookie2 = request.COOKIES.get('visitors_v2')
  return (cookie1, cookie2)


def set_cookies(visit, response):
  for cookie in visit.cookies_set.all():
    log.info('Setting {} to {!r}.'.format(cookie.name, cookie.value))
    cookie_attributes = {}
    for field in ('max_age', 'expires', 'path', 'domain', 'secure', 'httponly'):
      if hasattr(cookie, field):
        cookie_attributes[field] = getattr(cookie, field)
    response.set_cookie(cookie.name, cookie.value, **cookie_attributes)
  return response


def create_visit(request, visitor):
  visit = Visit(
    method=request.method,
    scheme=request.scheme,
    host=request.get_host(),
    path=request.path_info,
    query_str=request.META.get('QUERY_STRING') or request.GET.urlencode(),
    referrer=request.META.get('HTTP_REFERER'),
    visitor=visitor
  )
  visit.save()
  # Take care of the cookies received and sent.
  cookies_got, cookies_set = create_cookies_got_set(request.COOKIES)
  visit.cookies_got.add(*cookies_got)
  visit.cookies_set.add(*cookies_set)
  visit.save()
  return visit


def create_cookies_got_set(request_cookies):
  cookies_got = []
  for name, value in request_cookies.items():
    cookies_got.append(get_or_create_cookie('got', name, value))
  if request_cookies.get('visitors_v1') is None:
    cookie1_properties = {'name':'visitors_v1', 'value':make_cookie1(), 'max_age':COOKIE_MAX_AGE}
    cookie1 = get_or_create_cookie('set', **cookie1_properties)
    cookies_set = [cookie1]
  else:
    cookies_set = []
  return cookies_got, cookies_set


def get_or_create_cookie(direction, name=None, value=None, **attributes):
  matches = Cookie.objects.filter(direction=direction, name=name, value=value, **attributes)
  if name.startswith('visitors_v'):
    attr_str = ', '.join([key+'='+str(val) for key, val in attributes.items()])
    if attr_str:
      attr_str = ' ('+attr_str+')'
  if matches:
    if name.startswith('visitors_v'):
      log.info('Found {} existing cookies matching {} cookie {}={}{}'
               .format(len(matches), direction, name, value, attr_str))
    return matches[0]
  else:
    if name.startswith('visitors_v'):
      log.info('No match for {} cookie {}={}{}'.format(direction, name, value, attr_str))
    cookie = Cookie(direction=direction, name=name, value=value, **attributes)
    cookie.save()
    return cookie


def make_cookie1():
  # Make a legacy visitors_v1 cookie:
  # 16 random characters chosen from my own base64-like alphabet I chose long ago.
  return ''.join([random.choice(ALPHABET1) for i in range(16)])


def get_or_create_visitor(ip, cookies_got, user_agent):
  """Find a Visitor by ip, user_agent, and cookies sent (only visitors_v1/2).
  If no exact match for the Visitor is found, create one. In that case, if a Visitor with a matching
  cookie can be found, assume it's the same User."""
  cookie1, cookie2 = cookies_got
  visitor, user, label = get_visitor_user_and_label(ip, user_agent, cookie1, cookie2)
  if not user:
    user = User()
    user.save()
    log.info('Created new User (id {})'.format(user.id))
  if not visitor:
    visitor = Visitor(
      ip=ip,
      user_agent=user_agent,
      cookie1=cookie1,
      cookie2=cookie2,
      label=label,
      user=user,
      version=2,
    )
    visitor.save()
    log.info('Created a new Visitor (id {}).'.format(visitor.id))
  return visitor


def get_visitor_user_and_label(ip, user_agent, cookie1, cookie2):
  """Look for an existing Visitor matching the current one.
  Returns:
  visitor: Only an exact match (identical ip, user_agent, cookie1, and cookie2 fields).
    If multiple Visitors match, return the first one. If none match, return None.
  user: If an exact match, the User for that Visitor. If no exact match, look for Visitors with a
    matching cookie. If any are found, return the User for the first Visitor. Otherwise, return None.
  label: If an exact match, return the label for that Visitor. If no exact match, find Visitors with
    a matching cookie and return the common start of their labels. Otherwise, return an empty string.
  """
  # Does this Visitor already exist?
  visitor = get_exact_visitor(ip, user_agent, cookie1, cookie2)
  if visitor is None:
    # If no exact match, use the cookie(s) to look for similar Visitors.
    visitors = get_visitors_by_cookie(cookie1, cookie2)
    if visitors:
      user, label = pick_user_and_label(visitors)
      return None, user, label
    else:
      return None, None, ''
  else:
    return visitor, visitor.user, visitor.label


def get_exact_visitor(ip, user_agent, cookie1, cookie2):
  """Get a Visitor by exact match.
  It will find any Visitor with the same ip, user_agent, cookie1, and cookie2. If any of these are
  None, the field in the Visitor must be null too. If more than one match is found, the first will
  be returned. Returns None if no matches are found."""
  log.info('Searching for an exact match for ip: {!r}, visitors_v1: {!r}, visitors_v2: {!r}, and '
           'user_agent: {!r}..'.format(ip, cookie1, cookie2, user_agent))
  try:
    # An exact match?
    visitor = Visitor.objects.get(ip=ip, user_agent=user_agent, cookie1=cookie1, cookie2=cookie2)
    log.info('This Visitor already exists (id {}).'.format(visitor.id))
  except Visitor.MultipleObjectsReturned:
    # Multiple matches? This shouldn't happen, but just pick the first one, then.
    #TODO: Determine more intelligently which visitor to use.
    visitor = Visitor.objects.filter(ip=ip, user_agent=user_agent, cookie1=cookie1, cookie2=cookie2)[0]
    log.warn('Multiple Visitors found. Using first one (id {})'.format(visitor.id))
  except Visitor.DoesNotExist:
    log.info('No exact match found.')
    visitor = None
  return visitor


def get_visitors_by_cookie(cookie1, cookie2):
  """Search for Visitors by cookie (an "inexact" match).
  Try matching by cookie1 first. If cookie1 is None, or no match is found, try cookie2.
  Returns a list of matching Visitors."""
  if cookie1 is None and cookie2 is None:
    return None
  log.info('Searching for an inexact match for visitors_v1: {!r} or visitors_v2: {!r}.'
           .format(cookie1, cookie2))
  visitors = None
  if cookie1 is not None:
    visitors = Visitor.objects.filter(cookie1=cookie1)
    if visitors:
      log.info('Found {} Visitor(s) with visitors_v1 == {!r}'.format(len(visitors), cookie1))
  if cookie2 is not None and not visitors:
    visitors = Visitor.objects.filter(cookie2=cookie2)
    if visitors:
      log.info('Found {} Visitor(s) with visitors_v2 == {!r}'.format(len(visitors), cookie2))
  if not visitors:
    log.info('Found no Visitor with either cookie.')
  return visitors


def pick_user_and_label(visitors):
  # Take the label for the new visitor from the existing ones.
  labels = [visitor.label for visitor in visitors]
  label = get_common_start(labels)
  ellipsis = ', ...'
  if len(labels) <= 5:
    ellipsis = ''
  log.info('Using the label {!r}, derived from existing label(s): "{}"{}'
           .format(label, '", "'.join(labels[:5]), ellipsis))
  return visitors[0].user, label


def get_common_start(labels):
  """Example: get_common_start(['me and you', 'me and you at 1507', 'me and Emily']) -> 'me and'
  Ignores empty strings (adding an empty string to the above list would give the same result).
  """
  common_start = None
  for label in labels:
    if label == '':
      continue
    elif common_start is None:
      common_start = label.split()
    else:
      label_parts = label.split()
      common_start_new = []
      for part1, part2 in zip(common_start, label_parts):
        if part1 == part2:
          common_start_new.append(part1)
      common_start = common_start_new
  if common_start is None:
    return ''
  else:
    return ' '.join(common_start)


def decode_cookie(cookie):
  """Decode an Nginx userid cookie into a uid string.
  Taken from: https://stackoverflow.com/questions/18579127/parsing-nginxs-http-userid-module-cookie-in-python/19037624#19037624
  This algorithm is for version 2 of http://wiki.nginx.org/HttpUseridModule.
  This nginx module follows the apache mod_uid module algorithm, which is
  documented here: http://www.lexa.ru/programs/mod-uid-eng.html.
  """
  # get the raw binary value
  binary_cookie = base64.b64decode(cookie)
  # unpack into 4 parts, each a network byte orderd 32 bit unsigned int
  unsigned_ints = struct.unpack('!4I', binary_cookie)
  # convert from network (big-endian) to host byte (probably little-endian) order
  host_byte_order_ints = [socket.ntohl(i) for i in unsigned_ints]
  # convert to upper case hex value
  uid = ''.join(['{0:08X}'.format(h) for h in host_byte_order_ints])
  return uid


def encode_cookie(uid):
  """Encode a uid into an Nginx userid cookie.
  Reversed from decode_cookie() above."""
  unsigned_ints = []
  if len(uid) != 32:
    return None
  for i in range(0, 32, 8):
    host_byte_str = uid[i:i+8]
    try:
      host_byte_int = int(host_byte_str, 16)
    except ValueError:
      return None
    net_byte_int = socket.htonl(host_byte_int)
    unsigned_ints.append(net_byte_int)
  binary_cookie = struct.pack('!4I', *unsigned_ints)
  cookie_bytes = base64.b64encode(binary_cookie)
  return str(cookie_bytes, 'utf8')


# Bot detection:
#TODO: Put these in the database for more flexibility and possibly even a gain in speed.
# These names occur in a known location in the user_agent string: After "compatible; " and before
# "/" or ";", e.g.: Mozilla/5.0 (compatible; Exabot/3.0; +http://www.exabot.com/go/robot)
UA_BOT_NAMES = ('Googlebot', 'bingbot', 'Baiduspider', 'YandexBot', 'AhrefsBot', 'Yahoo! Slurp',
                'Exabot', 'Uptimebot', 'MJ12bot', 'Yeti', 'SeznamBot', 'DotBot', 'spbot', 'Ezooms',
                'BLEXBot', 'SiteExplorer', 'SEOkicks-Robot', 'WBSearchBot', 'SemrushBot',
                'SMTBot', 'Dataprovider.com', 'SISTRIX Crawler', 'coccocbot-web')
# These names occur after "compatible; " and before " ". It's incompatible with the above, which
# allows spaces in the names.
UA_BOT_NAMES_SPACE_DELIM = ('archive.org_bot',)
# For these, the user_agent string begins with the bot name, followed by a "/".
UA_BOT_STARTSWITH = ('curl', 'Sogou web spider', 'TurnitinBot', 'Wotbox', 'SeznamBot', 'Aboundex',
                     'msnbot-media', 'masscan')


def is_robot(visit):
  visitor = visit.visitor
  if not (visit.host or visit.query_str or visit.referrer or visitor.user_agent or visitor.cookie1
          or visitor.cookie2) and (visit.path == '/' or visit.path == ''):
    return True
  elif invalid_host(visit.host):
    return True
  else:
    return is_robot_ua(visitor.user_agent)


def invalid_host(host):
  """Check every level of subdomains to allow things like "www.nstoler.com" to match "nstoler.com".
  """
  domain = ''
  for subdomain in reversed(host.split('.')):
    if domain:
      domain = subdomain + '.' + domain
    else:
      domain = subdomain
    if domain in settings.ALLOWED_HOSTS:
      return False
  return True


def is_robot_ua(user_agent):
  if user_agent is None or user_agent == '':
    return True
  # Does the user_agent contain a known bot name in the standard position?
  ua_halves = user_agent.split('compatible; ')
  if len(ua_halves) >= 2:
    # Look for it after 'compatible; ' and before '/', ';', or whitespace.
    bot_name = ua_halves[1].split('/')[0].split(';')[0]
    if bot_name in UA_BOT_NAMES:
      return True
    # Check for bot names that contain whitespace (same as above, but don't split on whitespace)
    bot_name = bot_name.split()[0]
    if bot_name in UA_BOT_NAMES_SPACE_DELIM:
      return True
  # Does the user_agent start with a known bot name?
  fields = user_agent.split('/')
  if fields[0] in UA_BOT_STARTSWITH:
    return True
  # It's not a known bot.
  return False