# ETL4life
It's ETL all the way down isn't it?

# dictToDF
When converting dictionary data to a dataframe we compared:
Creating a list of dictionaries, Creating a dictionary of lists, creating a dictionary of lists with matching names
We found the following:
Average run time for createDummyUsersA over 1000 runs: 211 microseconds
Average run time for createDummyUsersB over 1000 runs: 194 microseconds
Average run time for createDummyUsersC over 1000 runs: 191 microseconds

With A being list of dictionaries
B being dictionary of lists with mapping
C being dictionary of lists with 1to1 naming

When looking at memory consumption, B and C consumed on average 4.52 KB while A only consumed 4.39 KB.
If for some reason you are strapped for memory, maybe lean towards version A

# Why not use squaredance script instead?
In real life you use the tech stack that exists. 
Building things in a language nobody else understands is instant technical bottleneck sedoku.
If python is there, use python.