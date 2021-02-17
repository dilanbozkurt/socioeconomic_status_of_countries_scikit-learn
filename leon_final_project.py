#IMPORTS

import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

#--------------GETTING THE DATA---------------

data = pd.read_csv("Country-data.csv")


#----------------PREPROCESSING---------------

print("---Checking the duplicated and null values---")

duplicate_check=sum(data.duplicated(subset = 'country')) == 0
print("True if there is no duplicated value:",duplicate_check)

print("--------------------------")

is_null=data.isnull().sum()
print("0 if there is no null value:")
print(is_null)

#According to factors, plotting the 10 countries that has the worst conditions

import matplotlib.pyplot as plt
import seaborn as sns

fig, axs = plt.subplots(3,3,figsize = (15,15))

columns_False=['child_mort','total_fer','inflation']
columns_True=['life_expec','health','gdpp','income','exports','imports']

axsFalse=[axs[0,0],axs[0,1],axs[0,2]]
axsTrue=[axs[1,0],axs[1,1],axs[1,2],axs[2,0],axs[2,1],axs[2,2]]

for column in range(3):
    for ax in axs:
        top10 = data[['country',columns_False[column]]].sort_values(columns_False[column], ascending = False).head(10)
        plt1 = sns.barplot(x='country', y=columns_False[column], data= top10, ax = axsFalse[column],palette="ch:s=-.2")
        plt1.set(xlabel = '', ylabel= columns_False[column])

for column in range(6):
    for ax in axs:
        top10 = data[['country',columns_True[column]]].sort_values(columns_True[column], ascending = True).head(10)
        plt1 = sns.barplot(x='country', y=columns_True[column], data= top10, ax = axsTrue[column],palette="ch:s=-.2")
        plt1.set(xlabel = '', ylabel= columns_True[column])
            
for ax in fig.axes:
    plt.sca(ax)
    plt.xticks(rotation = 90)
    
plt.tight_layout()
plt.savefig("worst_condition.pdf")
plt.close()


#-------------Plotting the Heatmap to see the correlations between variables---------------

plt.figure(figsize = (8,6))  
sns.heatmap(data.corr(),annot = True,cmap="Purples")
plt.savefig("heatmap.pdf")
plt.close()

#----------------Making import export and healt values looking like gdpp values, not percentage-----------------
for i in ['imports','exports','health']:
    data[i] = (data[i] * data['gdpp'])/100
    
    
#Standard scaler

from sklearn.preprocessing import StandardScaler

new_df = data[data.columns[data.dtypes != 'object']]

scaler = StandardScaler()
data_scaled = pd.DataFrame(scaler.fit_transform(new_df))

#-----------------CLUSTERING TENDENCY---------------------

from sklearn.neighbors import NearestNeighbors
from random import sample
from numpy.random import uniform
from math import isnan


def hopkins(X):
    d = X.shape[1]
    n = len(X) 
    m = int(0.1 * n) 
    nbrs = NearestNeighbors(n_neighbors=1).fit(X.values)
 
    rand_X = sample(range(0, n, 1), m)
 
    ujd = []
    wjd = []
    for j in range(0, m):
        u_dist, _ = nbrs.kneighbors(uniform(np.amin(X,axis=0),np.amax(X,axis=0),d).reshape(1, -1), 2, return_distance=True)
        ujd.append(u_dist[0][1])
        w_dist, _ = nbrs.kneighbors(X.iloc[rand_X[j]].values.reshape(1, -1), 2, return_distance=True)
        wjd.append(w_dist[0][1])
 
    H = sum(ujd) / (sum(ujd) + sum(wjd))
    if isnan(H):
        print(ujd, wjd)
        H = 0
 
    return H


print("------------------------")
print("Hopkins score:",hopkins(new_df))
print("------------------------")

#---------------Finding the optimum number of Clusters - Elbow Curve-------------------------

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

inertia_list = []
cluster_labels=[]

num_clusters = [2, 3, 4, 5, 6, 7, 8]

for num_cluster in num_clusters:
    kmeans = KMeans(n_clusters=num_cluster,max_iter=50)
    kmeans.fit(data_scaled)
    
    inertia_list.append(kmeans.inertia_)
    cluster_labels = kmeans.labels_
    silhouette_avg = silhouette_score(data_scaled, cluster_labels)
    print("For n_clusters={0}, the silhouette score is {1}".format(num_cluster, silhouette_avg))

df_inertia = pd.DataFrame(inertia_list)
df_inertia.columns = ['Inertia']

plt.plot(num_clusters, df_inertia['Inertia'], 'bx-',color='purple')

plt.title('Inertia/Elbow Curve')
plt.savefig('inertia.pdf')
plt.close()

print("--------------------------")

#------------------------------kMeans with 3 cluster---------------------

kmeans_3cluster = KMeans(n_clusters=3, init='k-means++', random_state=42).fit(data_scaled)
data['kmeans_3cluster_labels'] = kmeans_3cluster.labels_

#counting the number of the countries in each cluster
count0=0
count1=0
count2=0

for label in kmeans_3cluster.labels_:
    if(label==0):
        count0+=1
    elif(label==1):
        count1+=1
    else:
        count2+=1
    
print("0. cluster:",count0)
print("1.cluster:",count1)
print("2. cluster:",count2)

sns.scatterplot(x='income', y='child_mort', hue='kmeans_3cluster_labels',data=data, legend='full', palette="flare",s=100,alpha=0.7)
plt.savefig('3cluster.pdf')
plt.close()

print("--------------------------")

#------------------------kMeans with 4 cluster----------------------------

kmeans_4cluster = KMeans(n_clusters=4, init='k-means++', random_state= 42).fit(data_scaled)
data['kmeans_4cluster_labels'] = kmeans_4cluster.labels_

#counting the number of the countries in each cluster

count0=0
count1=0
count2=0
count3=0

for label in kmeans_4cluster.labels_:
    if(label==0):
        count0+=1
    elif(label==1):
        count1+=1
    elif(label==2):
        count2+=1
    else:
        count3+=1
    
print("0. cluster:",count0)
print("1. cluster:",count1)
print("2. cluster:",count2)
print("3. cluster:",count3)

sns.scatterplot(x='income', y='child_mort', hue='kmeans_4cluster_labels',data=data, legend='full', palette="flare",s=100,alpha=0.7)
plt.savefig('4cluster.pdf')
plt.close()

print("--------------------------")

#-----------------------------------kMeans with 5 cluster--------------------------------------

kmeans_5cluster = KMeans(n_clusters=5, init='k-means++', random_state= 42).fit(data_scaled)
data['kmeans_5cluster_labels'] = kmeans_5cluster.labels_

#counting the number of the countries in each cluster

count0=0
count1=0
count2=0
count3=0
count4=0

for label in kmeans_5cluster.labels_:
    if(label==0):
        count0+=1
    elif(label==1):
        count1+=1
    elif(label==2):
        count2+=1
    elif(label==3):
        count3+=1
    else:
        count4+=1
    
print("0. cluster:",count0)
print("1. cluster:",count1)
print("2. cluster:",count2)
print("3. cluster:",count3)
print("4. cluster:",count4)

sns.scatterplot(x='income', y='child_mort', hue='kmeans_5cluster_labels',data=data, legend='full', palette="flare",s=100,alpha=0.7)
plt.savefig('5cluster.pdf')
plt.close()

#WE DECIDED 4 CLUSTER

#-------------------------------INCOME-OTHER-----------------------------------

x1 =sns.pairplot(data, palette='flare', x_vars=['gdpp','exports','health','imports'], y_vars=['income'] ,diag_kind = None, hue='kmeans_4cluster_labels')
plt.savefig('income_other1.pdf')
plt.close()
x2 =sns.pairplot(data, palette='flare', x_vars=['child_mort','inflation','life_expec','total_fer'], y_vars=['income'] ,diag_kind = None, hue='kmeans_4cluster_labels' )
plt.savefig('income_other2.pdf')
plt.close()

#------------------------------------------------------------------------------

print("--------------------------")

analysis =  data.groupby(['kmeans_4cluster_labels']).mean()
analysis.drop(['kmeans_3cluster_labels','kmeans_5cluster_labels'],axis=1, inplace= True)

analysis['Number of countries']=data.groupby('kmeans_4cluster_labels')['country'].count()
print(analysis)

analysis['Percentage']=round((analysis['Number of countries']) / (analysis['Number of countries'].sum()),2)


#-----------------------------PIE CHART-------------------------------------------

labels = 'Cluster 0', 'Cluster 1', 'Cluster 2','Cluster 3'
sizes = analysis['Percentage']
colors = ["navajowhite","salmon","mediumvioletred","rebeccapurple"]

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%',shadow=True,colors=colors, startangle=90)

ax1.axis('equal') 
plt.savefig('pie_chart.pdf')
plt.close()
               
#---------------------------This lists hold the mean values of every criteria for 3 cluster-----------------------------

analysis.drop([2],axis=0, inplace= True)

child_mort_list=[]
exports_list=[]
health_list=[]
imports_list=[]
income_list=[]
inflation_list=[]
life_expec_list=[]
total_fer_list=[]
gdpp_list=[]

for i in analysis["child_mort"]:
    child_mort_list.append(i)
for i in analysis["exports"]:
    exports_list.append(i)
for i in analysis["health"]:
    health_list.append(i)
for i in analysis["imports"]:
    imports_list.append(i)
for i in analysis["income"]:
    income_list.append(i)
for i in analysis["inflation"]:
    inflation_list.append(i)
for i in analysis["life_expec"]:
    life_expec_list.append(i)
for i in analysis["total_fer"]:
    total_fer_list.append(i)
for i in analysis["gdpp"]:
    gdpp_list.append(i)    
    
#--------------------------------------STACKED BAR PLOT------------------------------------

plotdata1 = pd.DataFrame({
    "child_mort":child_mort_list,
    "inflation":inflation_list,
    "life_expec":life_expec_list,
    "total_fer":total_fer_list}, 
    index=["Cluster 0", "Cluster 1","Cluster3"])

plotdata1.plot(kind='bar', stacked=True,figsize=(10,10),color=['palevioletred', 'darkseagreen','teal', 'coral'])
plt.legend(loc='upper left')
plt.savefig('stacked1.pdf')
plt.close()

plotdata3 = pd.DataFrame({
    "income":income_list,
    "gdpp":gdpp_list, 
    "exports_list":exports_list,
    "imports":imports_list},
    index=["Cluster 0", "Cluster 1","Cluster3"])

plotdata3.plot(kind='bar', stacked=True,figsize=(10,10),edgecolor=None,color=['palevioletred', 'darkseagreen','teal', 'coral'])
plt.legend(loc='upper left')
plt.savefig('stacked2.pdf')
plt.close()


#----------------------------Printing the top 10 undeveloped countries----------------------------------

cluster_km=data[data['kmeans_4cluster_labels']==3]
cluster_km.sort_values(['gdpp','income','child_mort','health','inflation','life_expec','total_fer','imports','exports'], 
                      ascending=[True,True,False,True,False,True,False,False,True],inplace=True)


final_data=cluster_km.head(10).drop(['kmeans_3cluster_labels','kmeans_4cluster_labels','kmeans_5cluster_labels'],axis = 1)

print("Countries that have the worst conditions after the kMeans clustering: ")
print(final_data)

print("Country that has the best conditions after the kMeans clustering: ")
print(data[data['kmeans_4cluster_labels']==2])


sns.scatterplot(x='income', y='child_mort', hue='country',
                data=final_data, legend='full', palette="tab10", s=300)

sns.set(rc={'figure.figsize':(8,8)})
plt.savefig('top10.pdf')
plt.close()

#----------------------------To perform Hierarchical clustering----------------------------

from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import cut_tree

mergings = linkage(data_scaled, method="complete", metric='euclidean')
dendrogram(mergings)
plt.title('Hierarchical Clustering Dendrogram - Complete linkage',fontsize=20)
plt.xlabel('Country',fontsize=20)
plt.ylabel('Values',fontsize=20)
plt.savefig('hierarchical.pdf')
plt.close()

cluster_labels = cut_tree(mergings, n_clusters=6).reshape(-1, )
data['hierarcical_cluster_labels'] = cluster_labels

sns.scatterplot(x='income', y='child_mort', hue='hierarcical_cluster_labels',data=data, legend='full', palette="flare",s=100,alpha=0.7)
plt.savefig('hierarchical_6_cluster.pdf')
plt.close()

worst_top10 = data[data['hierarcical_cluster_labels'] ==0].sort_values(by =['gdpp','income','child_mort','health','inflation','life_expec','total_fer','imports','exports'], 
                      ascending=[True,True,False,True,False,True,False,False,True]) .head(10)

print("Countries that have the worst conditions after the hierarcical clustering: ")
print(worst_top10)

#-----------------------------CHECKING THE SOCIOECONOMIC SCORES GROWTH AFTER YEARS-----------------------

#Getting the SES data
year_data = pd.read_csv("GLOB.SES.csv",encoding='ISO-8859-1')

recent_data = year_data.loc[year_data["year"]==2010]

growth = []
for i in recent_data["country"]:
    lowest = year_data[year_data['country']==i].nsmallest(1, "SES")["SES"].values
    g = recent_data["SES"].loc[recent_data['country'] == i].values - lowest
    growth.append(g)
    
growth = np.array(growth, dtype=float)
recent_data["SES Growth"] = growth


worst_country_list=["Burundi","Liberia","Congo, Dem Rep","Niger","Sierra Leone","Madagascar","Mozambique","Central African Republic","Malawi","Eritrea"]

last_recent_data=recent_data.drop(['unid', 'wbid','year','SES','gdppc','yrseduc','popshare'], axis=1)
last_recent_data=last_recent_data.drop(['country'],axis=1)


cluster_labels2=[]
num_clusters2 = [2, 3, 4, 5, 6, 7, 8]

for num_cluster in num_clusters2:
    kmeans2 = KMeans(n_clusters=num_cluster,max_iter=50)
    kmeans2.fit(last_recent_data)
    
    cluster_labels2 = kmeans2.labels_

    silhouette_avg2 = silhouette_score(last_recent_data, cluster_labels2)
    print("For n_clusters={0}, the silhouette score is {1}".format(num_cluster, silhouette_avg2))
       
print("-------------------------------------------------")
print("Socioeconomic scores growth and k-means clusters of the top 10 underdeveloped countries: ")

ses_kmeans_4cluster = KMeans(n_clusters=6, init='k-means++', random_state= 42).fit(last_recent_data)
recent_data['ses_kmeans_4cluster'] = ses_kmeans_4cluster.labels_

recent_data=recent_data.drop(['unid', 'wbid','year','SES','gdppc','yrseduc','popshare'], axis=1)

worst_ses=pd.DataFrame()
for i in worst_country_list:
    worst_ses = worst_ses.append(recent_data.loc[recent_data["country"]==i], ignore_index=True)

print(worst_ses)

print("--------------------------------------------------------")

print("These countries have the highest socioeconomic scores growth: ")

print(recent_data.sort_values(by="SES Growth",ascending=False).head(7))

print("------------------------------------------------------------")

print("Is there a country you wonder about its level of development?")

select_country=str(input("Enter a valid country name (For example: China): "))

index=data[data['country']==select_country].index.values

for i in data['country']:
    if(i == select_country):
        if(data.at[index[0],'kmeans_4cluster_labels']==3):
            print("It is in cluster 3. It is a underdeveloped country.")
        elif(data.at[index[0],'kmeans_4cluster_labels']==1):
            print("It is in cluster 1. It is a developed country.")
        elif(data.at[index[0],'kmeans_4cluster_labels']==0):
            print("It is in cluster 0. It is a developing country.")
        else:
            print("It is in cluster 2. It is a developed country.")
            
country_list=[]
for i in data['country']:
    country_list.append(i)
if select_country not in country_list:
    print("There is no country like that.")
