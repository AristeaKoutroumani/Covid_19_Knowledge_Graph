import pandas as pd
#the pymed library is used to query the PubMed database and acquire article info
from pymed import PubMed
pubmed = PubMed(tool="PubMedRetriever", email="myemail@acg.edu")

#enter search term here, this acquires all the articles that appear when you search for the term in pubmed
search_term = "covid-19"
#enter the max number of results
search_results = pubmed.query(search_term, max_results=100000)
#create the lists that are used to save acquired data
article_list = []
article_details = []
abstracts=[]
qualitydata=[]
#create the identifiers that are used to identify and seperate the fields of interest
startdoi="|start_doi|"
enddoi="|end_doi|"
startpubmedid="|start_pid|"
endpubmedid="|end_pid|"
startpdate="|start_pd|"
endpdate="|end_pd|"

#go through all the articles that are retrieved by using the search term from pymed and save the information
for article in search_results:
# Convert each retrieved article to a dictionary
    article_dictionary = article.toDict()
    article_list.append(article_dictionary)

# Generate list of dictionary records which will hold all article details that could be fetched from PUBMED API
for article in article_list:
#get article pubmed ID
    pubmedId = article['pubmed_id'].partition('\n')[0]
    # Append all available article details to dictionary 
    try:
        article_details.append({u'pubmed_id':pubmedId,
                           u'title':article['title'],
                           u'keywords':article['keywords'],
                           u'journal':article['journal'],
                           u'abstract':article['abstract'],
                           u'conclusions':article['conclusions'],
                           u'methods':article['methods'],
                           u'results': article['results'],
                           u'copyrights':article['copyrights'],
                           u'doi':article['doi'],
                           u'publication_date':article['publication_date'], 
                           u'authors':article['authors']})
        
        #abstracts.append({u'abstract':article['abstract']})  
       
       #remove non ascii characters because semrep can't process them and produces an error, this also removes non-english results
       #add the seperators to identify the fields for publication date,doi and pubmed id when the triplets are created
       #these fields are used to associate each triplet with the article it came from
        qualitydata.append({u'abstract':article['abstract'].encode('ascii',errors='ignore'),
                           u'3.publication_date':startpdate+str(article['publication_date'])+endpdate,
                           u'2.doi':startdoi+article['doi']+enddoi,                           
                           u'1.pubmed_id':startpubmedid+pubmedId+endpubmedid})
    except:
        print("Invalid or incomplete article info")

# Generate Pandas DataFrame from list of dictionaries, the name quality is used because additional info is passed along with the raw text
quality_df= pd.DataFrame.from_dict(qualitydata)
#remove rows that contain null values
quality_df = quality_df[quality_df.astype(str).ne('None').all(1)]
#export the data to csv and json files, the csv file is processed by the semprep online batch processor at the next step
export_csv = quality_df.to_csv (r'pubmed_quality.csv', index = None, header=False)
#export_json= quality_df.to_json(r'pubmed_quality.json')

#the articles dataframe includes all article info
articles_df = pd.DataFrame.from_dict(article_details)
export_csv = articles_df.to_csv (r'pubmed_dataframe.csv', index = None, header=True)
#export_json= articles_df.to_json(r'pubmed_dataframe.json')

#abstracts_df= pd.DataFrame.from_dict(abstracts)
#export_csv = abstracts_df.to_csv (r'pubmed_abstracts.csv', index = None, header=False)
#export_json= abstracts_df.to_json(r'pubmed_abstracts.json')

