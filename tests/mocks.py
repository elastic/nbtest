import csv


def patched_sniff(self):
    print('This method has been monkey-patched!!')


csv.Sniffer.sniff = patched_sniff
