import pandas as pd

#this file is the output of semrep batch processor that contains the semantic triplets with the added information plus the flags
#pubmedQuery has to be run first and it's output should be batch processed using the semrep batch processor at https://ii.nlm.nih.gov/Batch/UTS_Required/semrep.shtml
#the resulting output file (text.out) is the input of this process for producing the semantic triplets in a form that can be imported to neo4j
filepath = 'covid-19.out'

#the identifiers are used to determine where the relevant text starts
#relation refers to the semantic triplet produced by semrep from the article abstracts
relation_identifier='|relation|'
#pubmedid is the first data quality information flag we attached to each article's abstract
pubmedid_identifier='|start_pid|'
#relations(triplets) and identifiers are saved in seperate lists but using a counter we can determine which relations belong to which identifier
relation_lines=[]
identifier_lines=[]
identifier_count=0
#seperators are used to seperate data parts (relations,identifiers)
seperator="|"

#create empty dataframes for the triplets and the identifiers (pubmedid,doi,publication_date)
column_names = ["subject", "predicate", "object","pubmed_id","doi","publication_date"]
triplets = pd.DataFrame(columns = column_names)
identifiers = pd.DataFrame(columns = ["pubmedid","doi","publication_date"])

#open the "out" file and read it line by line
with open(filepath) as fp:
   line = fp.readline()
   while line:      
       line = fp.readline()
       #if there is an identifier for the article metadata in the line add it to the list of identifiers and increase the identifier count
       if pubmedid_identifier in line:
           identifier_lines.append(line)
           identifier_count+=1
       #if a semrep relation is found in the line add the line in the relation lines list along with the identifier number (article metadata)
       if relation_identifier in line :
           relation_lines.append({u'identifier':identifier_count,
                                  u'relation':line})
    

#we created the identifiers and seperators for pubmedid,doi and publciation_date in a way that allows us to consistently retrieve
#them from every line
#the identifiers list contains the metadata for each article with a specific id that connects it to the retrieved relations
#since the splits are consistent using the seperator after testing it was determined exactly where the values are for each line
for r in identifier_lines :
    try:
        first = r.split(seperator)[2]
        second = r.split(seperator)[6]
        third = r.split(seperator)[10]
        new_row = {'pubmedid':first, 'doi':second, 'publication_date':third}
        identifiers=identifiers.append(new_row,ignore_index=True)
    except:
        print("invalid data or EOF")
        
        
#using the seperator | semrep uses for the relation format and the fact that the format remains constant for every relation
#we can split the lines to acquire subject predicate and object of the relation triplet
for r in relation_lines :
    try:
        subject = r['relation'].split(seperator)[3]
        predicate = r['relation'].split(seperator)[8]
        object = r['relation'].split(seperator)[10]
        identifier=r['identifier']-1
        pubmedid=identifiers.iloc[identifier][0]
        doi=identifiers.iloc[identifier][1]
        publication_date=identifiers.iloc[identifier][2]
        new_row = {'subject':subject, 'predicate':predicate, 'object':object , 'pubmed_id':pubmedid, 'doi':doi,'publication_date':publication_date}
        triplets=triplets.append(new_row,ignore_index=True)
    except:
        print("invalid data or EOF")
        
#export the semantinc triplets along with their specific identifiers (pubmedid,doi,publication_date) based on the article they came from
triplets.to_csv(r'triplets.csv', index = False)
#triplets.to_json(r'triplets.json')