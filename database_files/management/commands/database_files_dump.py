import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db.models import FileField, ImageField

from database_files.models import File
from database_files.utils import write_file, is_fresh

from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
#        make_option('-w', '--overwrite', action='store_true',
#            dest='overwrite', default=False,
#            help='If given, overwrites any existing files.'),
    )
    help = 'Dumps all files in the database referenced by FileFields ' + \
        'or ImageFields onto the filesystem in the directory specified by ' + \
        'MEDIA_ROOT.'

    def handle(self, *args, **options):
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        try:
            q = File.objects.all().values_list('id', 'name', '_content_hash')
            total = q.count()
            i = 0
            for (file_id, name, content_hash) in q:
                i += 1
                if not i % 100:
                    print '%i of %i' % (i, total)
                if not is_fresh(name=name, content_hash=content_hash):
                    print 'File %i-%s is stale. Writing to local file system...' \
                        % (file_id, name)
                    file = File.objects.get(id=file_id)
                    write_file(
                        file.name,
                        file.content,
                        overwrite=True)
        finally:
            settings.DEBUG = tmp_debug
            