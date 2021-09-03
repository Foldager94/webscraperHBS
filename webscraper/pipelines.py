# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
from itemadapter import ItemAdapter


class ItemPipeline:
    def process_item(self, item, spider):
        write_to_csv(item, spider.path)
        return item

def write_to_csv(item, path_to_csv):
    writer = csv.writer(open(path_to_csv, 'a', encoding="utf-8"), lineterminator='\n')
    writer.writerow([item[key] for key in item.keys()])
