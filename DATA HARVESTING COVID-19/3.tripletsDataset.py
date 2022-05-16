# Load the Pandas libraries with alias 'pd' 
import pandas as pd 


# Read data from files
#the articles dataframe contains all the info from the retrieved articles from pubmed using pubmedQuery.py
articles = pd.read_csv("pubmed_dataframe.csv") 
#the triplets dataframe contains the semantic triplets that were produced from tripletsProcessing.py
triplets = pd.read_csv("triplets.csv") 
#by merging the two datasets using the common identifiers "pubmed_id" we have all available article info for each triplet
triplets_full_info = pd.merge(triplets,articles, on = 'pubmed_id',how='inner')
#the file "All Journals in pubmed.txt" was downloaded from pubmed and contains ISSN information for the Journals in pubmed
filepath = 'All Journals in Pubmed.txt'

#this process creates a dataframe that contains the journal name and ISSN(print),ISSN(Online) information i a form it can be merged with
#the dataset of the triplets
column_names = ["journal", "ISSN(Print)", "ISSN(Online)"]
PubmedJournals = pd.DataFrame(columns = column_names)
#since the formating of the text file is consistent we can use some words as identifiers for the information that follows
JournalTitle_identifier = "journal"
ISSN_Print_identifier = "ISSN (Print)"
ISSN_Online_identifier = "ISSN (Online)"
#used to determine the cut off point where data is input on the dataframe
end_identifier = "--------------------------------------------------------"
inputline=[]
#open the file and read it line by line
with open(filepath) as fp:
   line = fp.readline()
   while line:      
       line = fp.readline()      
       if JournalTitle_identifier in line:
           #consistency of the file formatting allows to count the exact position of each word as well as the spaces
           JournalTitle=line[14:-1]
       if ISSN_Print_identifier in line:
           ISSNprint=line[15:]
           #removing the in the ISSN numbers for consistency with the other datasets
           ISSNprint=ISSNprint.replace('-','')
       if ISSN_Online_identifier in line:
           ISSNonline=line[15:]
           ISSNonline=ISSNonline.replace('-','')
       if end_identifier in line:
           inputline.append(
                {
                    'journal': JournalTitle,
                    'ISSN(Print)': ISSNprint,
                    'ISSN(Online)':  ISSNonline
                }
            )
           
PubmedJournals= pd.DataFrame(inputline)               
#export a dataset that contains the information for the pubmed journals in the form of journal,ISSN(Print),ISSN(Online)            
PubmedJournals.to_csv(r'PubmedJournals.csv', index = False)
#PubmedJournals.to_json(r'PubmedJournals.json')

#retain only the required information from the dataset
triplets_minimal= triplets_full_info[['subject','predicate','object','pubmed_id','doi_x','publication_date_y','journal']]

#merge the two datasets to associate ISSN to each triplet based on the journal name
triplets_minimal_ISSN=triplets_minimal.merge(PubmedJournals.drop_duplicates(subset=['journal']), how='left') 

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
sjr_minimal=sjr_minimal.rename(columns={"Rank":"SJR_rank","Title": "journal"})

#merging the triplets dataset that at this point contains article info and ISSN numbers of the journals with the SJR data that contains
#SJR rank info from scimagojr.com based on the journal title as well as the ISSN numbers results in the final dataset for the triplets
#this includes the semantic triplets (subject,predicate,object) article info (pubmed_id,doi,publication_date) and journal info (journal,ISSN,SJR and SJR_rank)
triplets_minimal_SJR=triplets_minimal.merge(sjr_minimal.drop_duplicates(subset=['journal','ISSN(Online)','ISSN(Print)']), how='left')

#rename the columns for clarity and consistency
triplets_for_neo4j=triplets_minimal_SJR.rename(columns={"publication_date_y":"publication_date","doi_x":"doi","ISSN(Online)":"issn_online","ISSN(Print)":"issn_print"})
#export the triplets with the additional quality info in a csv file that will be ready to be imported in neo4j 
triplets_for_neo4j.to_csv(r'triplets_for_neo4j.csv', index = False)
#triplets_for_neo4j.to_json(r'triplets_for_neo4j.json')
