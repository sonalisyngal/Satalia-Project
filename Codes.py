
#------------------------------------------------------------------------------
# Importing libraries
import pandas as pd
import networkx as nx
import numpy as np
import datetime
import matplotlib.pyplot as plt
%matplotlib inline

# Defining functions required
def isNaN(num):
    return num != num

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

bumb = pd.read_csv('data.csv') # your data for a particular project

# Removing messages not really writen by people:-------------------------------
bumb = bumb[bumb.message.str.contains("has joined the channel") == False]
bumb = bumb[bumb.message.str.contains("has left the channel") == False]
bumb = bumb.loc[(bumb['username']!='geekbot')]

# Creating matrix from which I will build network------------------------------
emp = list(set(bumb.username)) #List of employees 
mat = np.zeros(shape = (len(emp),len(emp)))
mat = pd.DataFrame(mat, columns = emp, index = emp) #Matrix for putting in values

# Adding aspect of people writing someone's name in message--------------------

# Creating column with only first name(since username is not exactly name for all)
bumb['name'] = bumb['fullname'].apply(lambda x: (x.split(" "))[0])


n = {k:0 for k in bumb.username} # Dictionary of names
for i in range(len(bumb.username)):
    n[bumb['username'].iloc[i]] = (bumb['name'].iloc[i]).split(" ")[0]
## PLease note:
# Using names (with capital) - there are names like Ed which will come in and '-- ed' word
# If people have the same name, further coding will have to be done. In my case
#  I didnt have employees with the same name.


# Loop for putting in weights in matrix for network----------------------------
for i in mat.index:
    data = bumb.loc[bumb.username == i] #Seeing data with only i person's messages
    mens = []
    for j in data.mentions: # Making a list of people mentioned by i 
        if isNaN(j) == False:
            mens.append(j) # List of people mentioned by person i 
    mens = ",".join(mens) # Converting list into string
    for k in mat.columns:
        mat.loc[i,k] = mens.count(k) + sum(data.message.str.contains(n[k]) == True) 
        # adding the number of times k is mentioned by i, and the number of messages in which k's name is called by i 
    mat.loc[i,i] = 0 # Removing instances when it comes as referred to himself(uploading file, sharing links etc)


# Building dataframe to build the network--------------------------------------
links = mat.stack().reset_index()
links.columns = ['from','to','weight']
links = links.loc[links['weight'] != 0]

# Building a weighted - directed graph-----------------------------------------
G = nx.from_pandas_dataframe(links, 'from','to',['weight'],create_using = nx.DiGraph())

# Page Rank of the nodes:
pgrnk1 = nx.pagerank(G)
pgrnk1 = dict(pgrnk1)

# Manipulation for the graph to look better (making the pgrank values negative - for better colour gradation in final network):
pg_n1 = {k:0 for k in pgrnk1.keys()}
for i in pgrnk1.keys():
    pg_n1[i] = -pgrnk1[i]

# Number of messages(attribute for node):
mess = {k:0 for k in G.nodes()}
for i in mess:
    data = bumb.loc[bumb.username == i]
    mess[i] = len(data)

# The Network graph Visualization--------------------------------------------------------
plt.figure(figsize=(23,10))
nx.draw_shell(G, with_labels = True,node_size = [m*13 for m in mess.values()], # can have with_labels = False (incase you dont want to show the names of employees)
                node_color = [c*2 for c in pg_n1.values()],cmap=plt.cm.winter, font_color ='black',
                font_size = 20,width = 0) 
plt.title('Employees in Project name',fontsize=30)


# The Prominence Distribution Visualization--------------------------------------------------------
p = []
for v in pgrnk1.values():
    p.append(v)
    
plt.hist(p,bins = 10)
plt.xlabel("Prominence Measure")
plt.ylabel("Count")

#------------------------------------------------------------------------------------------------

