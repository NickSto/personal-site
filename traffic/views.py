from django.shortcuts import render, redirect
from .lib import add_visit
from .models import Visit
import collections

PER_PAGE_DEFAULT = 50

def monitor(request):
  #TODO: Check for admin cookie and secure connection!
  # Get query parameters.
  params = request.GET
  page = int(params.get('p', 1))
  per_page = int(params.get('per_page', PER_PAGE_DEFAULT))
  include = params.get('include')
  # Calculate start and end of visits to request.
  if include == 'me':
    total_visits = Visit.objects.count()
  else:
    total_visits = Visit.objects.exclude(visitor__is_me=True).count()
  start_from_last = (page-1)*per_page + 1
  end_from_last = page*per_page
  end = total_visits - start_from_last + 1
  start = total_visits - end_from_last
  if start < 0:
    start = 0
  # Is this page beyond the last possible one?
  if page*per_page - total_visits >= per_page:
    # Then redirect to the last possible page.
    new_page = (total_visits-1) // per_page + 1
    #TODO: parameterize view and redirect to url name instead of redirecting to a literal path.
    return add_visit(request, redirect(_construct_monitor_path(new_page, include, per_page)))
  # Obtain visits list from database.
  if include == 'me':
    visits = Visit.objects.all()[start:end]
  else:
    visits = Visit.objects.exclude(visitor__is_me=True)[start:end]
  # Calculate some data for the template.
  if include == 'me':
    include_me = '&include=me'
  else:
    include_me = ''
  if total_visits > end_from_last:
    next_page = page+1
  else:
    next_page = None
  # debug = collections.OrderedDict()
  # debug['len(visits)'] = len(visits)
  # for var in ('total_visits', 'start', 'end', 'start_from_last', 'end_from_last'):
  #   debug[var] = vars()[var]
  context = {
    'current': page,
    'prev': page-1,
    'next': next_page,
    'start': start_from_last,
    'end': start_from_last+len(visits)-1,
    'include_me': include_me,
    # 'debug': debug,
    'visits': reversed(visits),
  }
  return add_visit(request, render(request, 'traffic/monitor.tmpl', context))

def _construct_monitor_path(page, include, per_page):
  path = '/traffic/monitor'
  if page > 1:
    path += '?p='+str(page)
  if include == 'me':
    path += '&include=me'
  if per_page != PER_PAGE_DEFAULT:
    path += '&per_page='+str(per_page)
  return path
