import csv

def process_csv(filename):
    exampleFile = open(filename, encoding="utf-8")  
    exampleReader = csv.reader(exampleFile) 
    exampleData = list(exampleReader)        
    exampleFile.close()  
    return exampleData
  
def flatten(some_list):
  collection=list()
  for item in some_list:
      if type(item)==list:
          collection.extend(flatten(item)) 
      else:
          collection.append(item)
  return collection

