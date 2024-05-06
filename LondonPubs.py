"""
Name: Brendan Harman
CS230: Section 1
Data: London Pubs
Description:
This program takes data about pubs in the uk and provides various statistical analysis and displays the results in visuals on streamlit
"""
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)


def readData():  # reads in data from csv
    '''
    @return a cleaned dataframe that contains all information to be used later
    '''
    data = "open_pubs_10000_sample.csv"
    # data = "test.csv"
    df = pd.read_csv(data, index_col = False, header = 0,

                      names = ["fsaID", "name", "address", "postcode",\

                               "easting", "northing","latitude","longitude",\

                               "localAuthority"])
    
    # clean data
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df.dropna(subset=["latitude", "longitude"], inplace=True)
    
    df["longitude"] = df["longitude"].astype(float)
    df["latitude"] = df["latitude"].astype(float)
    
    return df


def selectAuth(df):  # streamlit select authority
    '''
    @params passes the dataframe of pub data through
    @return a multi select box with all cities in an alphabetically sorted way capping the secection to 5
    '''
    # df = readData()
    df = sorted(df["localAuthority"].unique())
   
    return st.multiselect("Choose a city:", df, max_selections=5)


def singleAuth(df):  # streamlit select a single authority
    '''
    @params passes the dataframe of pub data through
    @return select box with all cities in an alphabetically sorted way
    '''
    # df = readData()
    df = sorted(df["localAuthority"].unique())
   
    return st.selectbox("Choose a city:", df)


def authFilter(selAuthority, df):  # filter data based on selected authority
    '''
    @params passes dataframe with pub data and a multiselect box
    @return dataframe of the selections from multi select box
    '''
    # df = readData()
    df = df.loc[df["localAuthority"].isin(selAuthority)]
    
    # print(df)
    return df


def authSelect(selAuthority, df):  # pick out the data from singleAuth
    '''
    @params passes dataframe with pub data and a single select box
    @return dataframe of the selected pub data
    '''
    # df = readData()
    df = df.loc[df["localAuthority"] == selAuthority]
    
    # print(df)
    return df


def mappingAuth(selAuthority, df):  # map pubs based on authority selection
    '''
    @params passes dataframe with pub data and single selectbox
    @return generates a map of pub locations
    '''
    df = authSelect(selAuthority, df)
    # print(df)
    df = df[["name", "address", "latitude", "longitude", "localAuthority"]]
    
    viewState = pdk.ViewState(latitude=df["latitude"].mean(),
                              longitude=df["longitude"].mean(),
                              zoom=11,
                              pitch=0)
    
    layer = pdk.Layer("ScatterplotLayer",
                      data=df,
                      get_position='[longitude, latitude]',
                      get_radius=200,
                      get_color=[150, 50, 250],
                      pickable=True,
                      opacity=.75,
                      radius_min_pixels=1,
                      radius_max_pixels=20,
                      radius_scale=1,
                      filled=True,
                      stroked=True,
                      line_width_min_pixels=1,
                      get_line_color=[0, 0, 0])
    
    tool_tip = {"text": "{name} \n{address}",
                "style": { "backgroundColor": "grey",
                            "color": "white"}}
    
    pubMap = pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11',
                   initial_view_state=viewState,
                   layers=[layer],
                   tooltip=tool_tip
                   )
    st.pydeck_chart(pubMap) 


def numPubsCity(selAuthority, df):  # count the number of pubs in each city
    '''
    @params passes a multiselect box and dataframe of pub data
    @return dictionary of cities and the count of pubs in them
    '''
    df = authFilter(selAuthority, df)
    
    cities = [row["localAuthority"] for index, row in df.iterrows()]
    
    dict = {}
    
    for city in cities:
        dict[city] = df["localAuthority"].value_counts()[city]
        
    return dict

       
def genBarChart(barDict):  # bar chart of pubs in each city
    '''
    @params passes dictionary of cities and count of pubs
    @return barchart of the cities of count
    '''
    x = barDict.keys()
    y = barDict.values()
    
    if barDict == {}:
        x = ["City of London", "Oxford", "Manchester"]
        y = [41, 19, 60]
    
    barChart = plt.bar(x, y, color="darkseagreen", edgecolor="black")
    plt.bar_label(barChart, label_type='edge')
    plt.xlabel("Cities")
    plt.ylabel("Count")
    
    return plt


def numPubsArea(order, df):  # count number of pubs in each area code
    '''
    @params order of the filter, top vs bottom postcodes and the dataframe of pub data
    @return dictionary of postcodes and the count of pubs in each
    '''
    # df = readData()
    df["postcode"] = df["postcode"].str[:3]
    # print(df)
    areaCodes = [row["postcode"] for index, row in df.iterrows()]

    codedict = {}

    topUser = st.slider("How many postcodes do you wish to see?", 3, 10)
    for code in areaCodes:

        codedict[code] = df["postcode"].value_counts()[code]
    topDict = dict(sorted(codedict.items(), key=lambda x: x[1], reverse=True) [:topUser]) 
    bottomDict = dict(sorted(codedict.items(), key=lambda x: x[1], reverse=False) [:topUser]) 
    
    if order == "bottom":
        returnDict = bottomDict
    else:
        returnDict = topDict
    # print(codedict)
    return returnDict


def genBarChart_AreaCode(areacodeDict):  # bar chart of pubs in each area code
    '''
    @params dictionary of areacodes and the count of pubs in each
    @return barchart of the pubs and their counts
    '''
    x = areacodeDict.keys()
    y = areacodeDict.values()

    barChart = plt.bar(x, y, color="cornflowerblue", edgecolor="black")
    plt.bar_label(barChart, label_type='edge')
    plt.xlabel("Postcodes")
    plt.ylabel("Count")

    return plt


def distance(lat1, long1, lat2=51.507924, long2=-0.087782):  # convert lat and long to distance from london bridge 
    # found distance formula from geeks for geeks website 
    '''
    @params latatude and longitudes of various pub locations and a default locations that is the london bridge
    @return distance in miles
    '''
    df = readData()

    lat1 = np.radians(lat1)
    long1 = np.radians(long1)
    lat2 = np.radians(lat2)
    long2 = np.radians(long2)
    
    dlong = long2 - long1
    dlat = lat2 - lat1
    
    dist = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlong / 2) ** 2
    distance = 2 * np.arcsin(np.sqrt(dist))
    distance *= 3956
    return distance


def withinRange(df):  # apply distance formula
    '''
    @params dataframe of pub data
    @return dataframe with a new distance column calculated based on distance function
    '''
    # df = readData()
    df["distance"] = distance(df["latitude"], df["longitude"])
    return df


def dataInRange(df):  # streamlit all pubs in whatever mile radius of london bridge
    '''
    @params dataframe of pub data
    @return generates a dataframe of the pubs within a certance distance
    '''
    dist = st.slider("Enter distance:" , 0, 10, value=2)
    df = withinRange(df)
    df = df.loc[df["distance"] <= dist]
    df = df.loc[:, ["name", "address", "distance"]]
    count = df.count()
    count = count[0]
    st.write("Total pubs within " + str(dist) + " miles of London Bridge: " + str(count))
    st.dataframe(df, hide_index=True, use_container_width=True, height=560)
    
    
def homePage():  # home page describing contents of app
    '''
    Provides an intro to the app and what is included in it
    '''
    st.title("London Pubs")
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e8/Churchill_Arms%2C_Kensington%2C_W8_%287459617058%29.jpg")
    st.subheader("Welcome to all of the UK Pub information you could ever want!")
    st.write("The UK is home to many pubs across mostly all cities, explore their locations on a map, counts in various cities and towns, psotcodes with the most and least amount of pubs, and lastly final a list of all pubs in a certain distance from the London Bridge!")
    

def tester():
    df = readData()
    
    # mapping
    # selAuthority = selectAuth()
    # mappingAuth(selAuthority)
    
    # print(selAuthority)
    # selAuthority = df["localAuthority"]
    # print(authFilter(selAuthority)
    # print(numPubsCity(selAuthority))
    
    # one chart at a time
    # st.pyplot(genBarChart(numPubsCity(selAuthority)))
    # st.pyplot(genBarChart_AreaCode(numPubsArea()))
    
    # distance
    # withinRange()
    # dataInRange()
    
    return


def main():
    '''
    Calls all functions based on certain conditions in streamlit
    '''
    st.set_page_config('London Pubs', page_icon="🍺", initial_sidebar_state="expanded",
        menu_items={
        'About': "This app demonstrates various Python techniques such as Pandas, Streamlit, Matplotlib, and other native Python functions. This also uses a database about London Pubs"
    })
    options = ["Home", "Map", "Pub Count", "Distance to London Bridge"]
    
    df = readData()
    display = st.sidebar.radio("Pick display", options=options)
    
    if display == "Home":
        homePage()
        
    elif display == "Map":
        st.header("Location of pubs based on city:")
        selAuthority = singleAuth(df)
        mappingAuth(selAuthority, df)
        st.write("This map shows the locations of all pubs in " + str(selAuthority) + ". The pubs name and addresses are provided with a hover click.")
    
    elif display == "Pub Count":
        st.header("Number of pubs based on city or postcode:")
        options = ["City", "Postcode"]
        
        chart = st.selectbox("Pubs per city or postcode?", options=options)
        
        if chart == "City":
            selAuthority = selectAuth(df)
            cityString = ""
            for city in selAuthority:
                cityString += (", " + city)
            if cityString == "":
                cityString = ", City of London, Oxford, Manchester"
            barDict = numPubsCity(selAuthority, df)
            st.pyplot(genBarChart(barDict))
            st.write("This chart shows how many pubs are in" + cityString + ".")
            
        elif chart == "Postcode":
            order = st.toggle("Toggle on for postcodes with the least pubs, off for postcodes with the most.",)
            if order:
                order = "bottom"
            else: 
                order = "top"
            postcodeDict = numPubsArea(order, df)
            st.pyplot(genBarChart_AreaCode(postcodeDict))
            st.write("This chart shows postcodes with the most or least pubs inside them.")
    
    else:
        st.header("List and count of pubs in a certain radius of London Bridge: ")
        withinRange(df)
        dataInRange(df)


# tester()
main()
