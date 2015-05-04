from django.core.management.base import BaseCommand
from autotag import autotag
from facebook_feeds.models import Facebook_Status
import math
from random import shuffle

NUM_OF_NEGATIVE_OR_POSITIVE_STATUSES = 100


class Command(BaseCommand):
    help = "Train the classifier for a given tag id."
    args = '<tag_id>'

    def handle(self, *args, **options):
        print 'start.'
        # all_statuses = Facebook_Status.objects.filter(tagged_items__isnull=False).order_by('?')
        # train_statuses = all_statuses[0:int(math.floor(all_statuses.count() / 2.0))]
        # test_statuses = all_statuses[int(math.floor(all_statuses.count() / 2.0)):]
        # print all_statuses.count()
        if len(args) == 0:
            raise Exception('Missing Tag ID')
        elif len(args) > 1:
            raise Exception('Too many Tag IDs')

        tag_id = args[0]

        positive_statuses = Facebook_Status.objects.filter(tagged_items__tag__id=tag_id)
        negative_statuses = Facebook_Status.objects.filter(tagged_items__isnull=False).exclude(
            tagged_items__tag__id=tag_id).order_by('?')[:NUM_OF_NEGATIVE_OR_POSITIVE_STATUSES]

        if positive_statuses.count() > NUM_OF_NEGATIVE_OR_POSITIVE_STATUSES:
            positive_statuses = positive_statuses[:NUM_OF_NEGATIVE_OR_POSITIVE_STATUSES]
        else:
            negative_statuses = negative_statuses[:len(positive_statuses)]

        status_data = []
        for status in positive_statuses:
            status_dict = {'id': status.id, 'text': status.content,
                           'tags': [str(tag.tag.id) for tag in status.tagged_items.all()]}
            status_data.append(status_dict)

        for status in negative_statuses:
            status_dict = {'id': status.id, 'text': status.content,
                           'tags': [str(tag.tag.id) for tag in status.tagged_items.all()]}
            status_data.append(status_dict)

        shuffle(status_data)

        train_statuses = status_data[0:int(math.floor(len(status_data) / 2.0))]
        test_statuses = status_data[int(math.floor(len(status_data)) / 2.0):]

        print 'length of data: train: %d, test: %d' % (len(train_statuses), len(test_statuses))
        at = autotag.AutoTag()
        print 'start training.'
        at.classify(train_statuses)
        print 'finished classifying! Start testing'

        a = at.test(test_statuses)
        print a
        print 'done.'

