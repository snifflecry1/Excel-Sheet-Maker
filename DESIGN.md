# Layout of app

- The app implementation used here revolves around
    - REST endpoints to create and export CSVs
    - a persistent websocket connection to handle live sheet updates
        - I implemented one of the requirements for simple formula addition that can be done in the format =followed by any sequence of addition or subraction mixed e.g =A1+A2-B2
    - Celery is used to 
        - Persist sheet updates in PostGres once they've been updated in server memory prior
        - Kick off a job to download the csv from the browser

# Tech choices

- Although it wasnt mentioned in the initial readme to use websockets, I thought having a peristed connection open per sheet was more efficent when handling sheet updates over trying to send http requests per cell update which doesn't scale as we add more users hitting the server

- My main priority to keep cell updates on the UI snappy was to cache each new sheet created in server memory and access it from there instead of pulling from PostGres every time, hence why I used dataclasses to handle the relationship between sheet and sheet cells in a clear, coherent manner when adding objects to this cache

- The app asychronously persists to PostGres in the background because I wanted to abstract client write and reads from db writes and reads which is more scalable in cases where we have thousands of users editing sheets

- I used AI to code up the client to wire it up to the backend but obviously understand how the React setup works. I mostly used AI as general skeleton guide when looking at the backend aided by several other sites online ranging from geeksforgeeks, aws docs and more.

# Future improvements 

- My tests only looks at a few views from views.py in a production setting, test coverage would usually range over 90% from my previous role so more coverage is a must here
- Right now when a spreadsheet is created, if the sheet is 40x40 there are 160 rows added to the spreadsheetcells table that have null values, this is probably very inefficient when in reality we only need to store the row and column data that actually has values and leave the client figure out any rows with no data and output this as blank lines, this in turn saves a lot of memory in PostGres
- Unimplemented nice to haves I obviously would have loved to build. 
    - Renaming the spreadsheet would be pretty straight forward in terms of an extra endpoint to send a PATCH update to the spreadsheets table
    - Adding and removing columns seems tricky since at the moment each cell of a spreadsheet is stored in a dictionary for fast access, inserting in between rows or colums would cause a shift of one row or col for every row col after, once that reprocessing was done this dictionary storing cell values would need to be updated and synced with the client too
    - Importing from a CSV could be as simple as adding functionality to read from a file, store the sheet in a dataclass and adding a new db method to create sheet from file but you would need to account for corrupt csv's before writing to PostGres for some robustness

- One useful addition to this app could be using redis (outside of its use with celery here) to cache the sheet server side too, this way we could have a source of truth at server without reading from PostGres and could add functionality for multiple users editing the same sheet

# Conclusion

- All in all I really enjoy making this app, It got me exposure to Celery and how that works with Redis and I even got some decent learning for using monkey patching to get websockets to work in a RESTful way. Would love to learn more of how such tech is used at Morta.
