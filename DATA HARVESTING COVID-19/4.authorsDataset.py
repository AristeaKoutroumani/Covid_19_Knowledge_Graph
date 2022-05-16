import pandas as pd
import ast

#import the dataframe the contains the information for all the articles acquired from pymed
pubmed_dataframe = pd.read_csv("pubmed_dataframe.csv") 

#retain only the relevant information for the authors in a smaller dataframe
df = pubmed_dataframe[['journal','authors','pubmed_id','title','doi','publication_date']]

#create a dataframe for the authors
column_names = ["author_firstname","author_lastname","author_name","journal","pubmed_id","title","doi","publication_date"]
authors_journals= pd.DataFrame(columns = column_names)

#go throuh each line (article) and acquire the relevant info as well as the author names
#the author names are in a dictionary that usually contains more than one name which is split on first name and last name
#the goal of this for loop is to assign the article information to each author seperately
#for example if an article has 5 authors in the pubmed_dataframe it is represented in one line but this process would result in 5 seperate entries
inputline=[]
for i, row in df.iterrows():
    journal = (df.loc[i,'journal'])
    pubmed_id = (df.loc[i,'pubmed_id'])
    title = (df.loc[i,'title'])
    doi = (df.loc[i,'doi'])
    publication_date = (df.loc[i,'publication_date'])
    authors=ast.literal_eval(df.loc[i,'authors'])
    #for each author acquire the first name and the last name as well as name (firstname+lastname) 
    for x in range(0, len(authors)):
        firstname=authors[x]['firstname']
        lastname=authors[x]['lastname']
        try:
            name = firstname + ' ' + lastname
            inputline.append(
                    {
                        'author_firstname':firstname,
                        'author_lastname': lastname,
                        'author_name' : name,
                        'journal':  journal,
                        'pubmed_id' : pubmed_id, 
                        'title' : title,
                        'doi':  doi,
                        'publication_date' : publication_date 
                    }
                )
        except :
             pass        
authors_journals= pd.DataFrame(inputline) 

#SJR data acquired from https://www.scimagojr.com/journalrank.php containing Journal ranks from 2019 (2020 is not available yet)
sjr_data=pd.read_csv("Journal_Citations(from SJR)_2019.csv",delimiter=';')
#replace - that indicates no number with a single comma for the code to realise there is no data in both fields
sjr_data['Issn'] = sjr_data['Issn'].str.replace('-','')
#having more than 3 values in the issn field creates an error when splitting
sjr_data=sjr_data[sjr_data.Issn.str.count(',').lt(2)]
#online is first then print
sjr_data[['ISSN(Online)','ISSN(Print)']] = sjr_data.Issn.str.split(",",expand=True,)
#retain only the required info from the dataset and rename them for consistency with the other datasets as well as clarity of information
sjr_minimal = sjr_data[['Rank','Title','ISSN(Online)','ISSN(Print)','SJR']]
sjr_minimal=sjr_minimal.rename(columns={"Rank":"SJR_rank","Title": "journal","ISSN(Online)":"issn_online","ISSN(Print)":"issn_print"})

#by combining the authors dataset with the SJR data each author (identified by name) has a seperate line for each article he has contributed in
#along with the SJR ranking of the journal each article was published in 
authors_SJR=authors_journals.merge(sjr_minimal.drop_duplicates(subset=['journal']), how='left')

#export the authors and the info of the article each one has contributed in with quality info in a csv file that will be ready to be imported in neo4j 
authors_SJR.to_csv(r'authors_for_neo4j.csv', index = False)
#authors_SJR.to_json(r'authors_SJR.json')
