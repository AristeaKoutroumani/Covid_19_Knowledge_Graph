
import pandas as pd

#import the dataframe the contains the information for all the articles acquired from pymed
pubmed_dataframe = pd.read_csv("pubmed_dataframe.csv")    
#import the dataframe the contains the information for the journals of the pubmed articles (ISSN numbers)
pubmed_journals = pd.read_csv("PubmedJournals.csv")       
             
#merging the two datasets associates the ISSN numbers for the journal each article was published in
pubmed_journals_ISSN=pubmed_dataframe.merge(pubmed_journals.drop_duplicates(subset=['journal']), how='left') 

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


#merging the articles dataset that at this point contains article info and ISSN numbers of the journals with the SJR data that contains
#SJR rank info from scimagojr.com based on the journal title as well as the ISSN numbers results in the final dataset for the articles and their relation to journals
pubmed_journal_SJR=pubmed_journals_ISSN.merge(sjr_minimal.drop_duplicates(subset=['journal','ISSN(Online)','ISSN(Print)']), how='left')

#rename the columns for clarity and consistency
pubmed_journal_SJR=pubmed_journal_SJR.rename(columns={"publication_date_y":"publication_date","doi_x":"doi","ISSN(Online)":"issn_online","ISSN(Print)":"issn_print"})

#export the dataset containing the articles,the journals they were published in and their SJR ranking information in a csv file that will be ready to be imported in neo4j
pubmed_journal_SJR.to_csv(r'articles_journals_for_neo4j.csv', index = False)
#pubmed_journal_SJR.to_json(r'pubmed_journal_SJR.json')