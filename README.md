# MSBA-6330
This project repository is created in partial fulfillment of the requirements for the Big Data Analytics course offered by the Master of Science in Business Analytics program at the Carlson School of Management, University of Minnesota.

In this project titled, "Streaming Data Analysis using Multi Cloud Strategy" we demonstrate one of the highly talked about topics in Cloud Computing according to Gartner Hype cycle for 2021, Multi Cloud Technology. We start off by presenting the definition of mutlicloud and its benefits to answer the question of why more and more companies should apply this approach to their business. Next, we introduced the specific use case to demonstrate the technology. Using mutlicloud strategy, we analyzed real-time stock price data for the most trending stocks according to WallStreetBets subreddit. For this, we used the Reddit API and the Yahoo Finance API available in python. In the Reddit API we extracted stock symbols from the top trending posts on the Wall Street Bets Subreddit. Next we used these trending stock symbols with the Yahoo Finance API to gather fields to use in our analysis. When it comes to the data actual pipeline, we used Azure and Google Cloud Platforms. On Azure side, we used Azure Events hub to pull data from python, Azure Stream Analytics to convert this event data to SQL and finally Blob Storage to store the data as files. On Google Cloud side, we used Data Transfer Service to get data from Azure and stored in Google Cloud Storage Bucket, which becomes the source of data for our visualizations in Google Data studio. As concluding remarks, we identified the biggest pros and cons of using multi cloud to give the companies a better sense of they would be dealing with.

![image](https://user-images.githubusercontent.com/59077721/167015812-d88e9f73-5068-46fc-83b9-99b9f1fff0f3.png)


Please check out our presentation video here: https://youtu.be/iZopI_Rtcw0

Check out our Flyer here: https://drive.google.com/file/d/1kXkFT26MzbvqWqD0yU8srm_hQAzvkmUS/view?usp=sharing

Gartner Hype Cycle for Cloud Computing in 2021 showing Multi Cloud at the "peak of inflated expections" : https://www.gartner.com/interactive/hc/4003590?ref=solrAll&refval=324960013

Please check out the set up instructions on InstructionManual.pdf file and the python script pythontoazure.py to replicate this project.

Please reach out to us if you have any questions.

Our Team: 
AnkurAggarwal aggar158@umn.edu
Garett Carlblom carlb050@umn.edu
Yan Dong dong0248@umn.edu
Pranitha Peddi peddi024@umn.edu
Gayathri Ramanathan raman141@umn.edu
