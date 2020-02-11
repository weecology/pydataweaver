# Schorn, Markus Erhard <markus.schorn@idiv.de>
# a) a tree-level datafile
# - one row for each measurement (i.e. if a tree was remeasured once, the file contains two lines for this tree)
# - each row contains a unique tree ID, which is the same for all measurements of a single tree (currently not the case in raw FIA data)
# - each row contains a unique plot ID, which is the same for all the trees in a single plot and for all the measurements of those trees, matching the plot ID in the plot-level datafile (see below)
# - if possible, data from plot-level datafile (important columns as mentioned below) already merged in this file 
# b) a plot-level datafile
# - in the best case one file containing merged data from XX_PLOT.csv and XX_COND.csv
# - important columns for me: FORTYPCD, STDAGE, SITECLCD from XX_COND.csv; INVYR, MEASYEAR, MEASMON, MEASDAY from XX_PLOT.csv; but it could be all the columns from both XX_PLOT.csv and XX_COND.csv as well
# - one row for each census
# - each row contains a unique plot ID (see above)
# I need this for data from WA and OR. For training purposes, the data could be filtered for FORTYPCD == 201 already, but I'd rather have the full dataset and do that myself later on. Also you could filter for remeasured plots only, but the same applies here. 

####### My Approach #######
### 1. prepare a data frame with plot and condition information merged:
###   1.1 read plot table to "plt" data frame and only keep ID columns (CN, PREV_PLT_CN) and other fields of interest to the user
###   1.2 read condition table to "cond" data frame and only keep ID columns (CN, PLT_CN, CONDID) and other fields of interest to the user
###   1.3 from the condition data frame "cond", get the number of conditions for each plot
###   1.4 add the number of conditions infomation to the plot data frame "plt", and name the field "ncond"
###   1.5 merge plot data frame "plt" with condition data frame "cond" based on plot's ID (e.g., CN in plt, PLT_CN in cond); call the new data frame "plt_cond"
### 2. prepare the tree data frame, which contains a field of unique tree ID which is same as the tree's CN when it was surveyed for the first time and keeps unchnaged in later surveys:
###   (The overall goal is as mentioned above. It is not neceesary to follow the same algorithm as I described in 2.1-2.4)
###   2.1 read tree table to "tree" data frame
###   2.2 prepare two data frames "tree_CN" and "cp" to save tree's raw ID columns (CN, PREV_TRE_CN) and initialize two new ID fields (ID0, ID1) with row order number in "tree" data frame
###   2.3 with a while loop, iterate the process of merging "tree_CN" and "cp" data frames to update the new tree ID1 field in the data frame "cp" with earlier ID0, until no previous tree record can be found
###   2.4 use ID0 and ID1 in data frame "cp" to identify the earliest tree's CN for each tree; and use that CN as the tree's unique ID (with field name of "ID") in tree data frame "tree"
### 3. create the merged data frame, with tree, plot, and condition ID fields conbined:
###   3.1 merge the data frame "tree" with data frame "plt_cond" based on plot and condition IDs (PLT_CN, CONDID); call the new data frame "tree_plot"
###   3.2 save "tree_plot" to a csv file
###   3.3 if the user needs more detailed info of plot and/condition, (s)he can use PLT_CN and/or COND_CN to link raw plot and condition tables

#plt <- read.csv('~/ufrc_hpc/FIA_1.6.1_20180110/PLOT.csv',stringsAsFactors=F)
plt <- read.csv('plot.csv',stringsAsFactors=F)
for(fld in c('CN','PREV_PLT_CN')) plt[,fld] <- as.character(plt[,fld])
plt <- plt[,c('CN','PREV_PLT_CN')]   # keep CN, PREV_PLT_CN + others

#cond <- read.csv('~/ufrc_hpc/FIA_1.6.1_20180110/COND.csv',stringsAsFactors=F)
cond <- read.csv('cond.csv',stringsAsFactors=F)
for(fld in c('CN','PLT_CN')) cond[,fld] <- as.character(cond[,fld])
cond <- cond[,c('CN','PLT_CN','CONDID')]     # keep CN, PLT_CN, CONDID + others
plt_cond_num <- with(cond,aggregate(CONDID,by=list(PLT_CN=PLT_CN),length))  # get number of condition information
names(plt_cond_num)[2] <- 'ncond'
plt <- merge(plt,plt_cond_num,by.x='CN',by.y='PLT_CN',all.x=T)    # add number of condition info to plt
plt_cond <- merge(plt,cond,by.x='CN',by.y='PLT_CN',all.x=T)       # plot + condition data frame
names(plt_cond)[which(names(plt_cond)=='CN.y')] <- 'COND_CN'      # make field name meaningful
names(plt_cond)[which(names(plt_cond)=='CN')] <- 'PLT_CN'         # make field name meaningful

state <- 'OR'   # choose state
tree <- read.csv(sprintf('~/ufrc_hpc/FIA_1.6.1_20180110/%s_TREE.csv',state),stringsAsFactors=F)
for(fld in c('CN','PLT_CN','PREV_TRE_CN')) tree[,fld] <- as.character(tree[,fld])

tree_CN <- tree[,c('CN','PREV_TRE_CN')]
tree_CN$ID0 <- 1:nrow(tree_CN)  # ID0 is the row order number, used to identify the raw record in "tree" data frame
cp <- tree_CN     # cp is a temporary data frame for identifying the corresponding row of the earliest record of a specific tree
cp$ID1 <- cp$ID0  # initialize two fields ID0 and ID1
# the following loop is to identify the earliest tree records by using the fields CN and PREV_TRE_CN in tree data frame
# One could find his own way to accomplish this task
while(with(cp,length(intersect(CN,PREV_TRE_CN))>0)) {
  cp <- merge(cp,tree_CN,by.x='PREV_TRE_CN',by.y='CN',all.x=T,suffixes=c('_pre','_post'))
  i_row <- which(is.na(cp$ID0_post))
  if(length(i_row)>0) cp$ID0_post[i_row] <- cp$ID1[i_row]
  i_row <- which(is.na(cp$PREV_TRE_CN))
  if(length(i_row)>0) cp$PREV_TRE_CN[i_row] <- cp$CN[i_row]
  cp <- cp[,c('ID0_pre','PREV_TRE_CN','PREV_TRE_CN_post','ID0_post')]
  names(cp) <- c('ID0','CN','PREV_TRE_CN','ID1')
}
cp <- cp[order(cp$ID0),c('ID0','ID1')]      # at this stage, cp contains the information of the raw row (ID0) and the corresponding row (ID1) for the tree's earliest record
tree <- cbind(ID=tree_CN$CN[cp$ID1],tree)   # use the earliest (first-survey) CN as tree's ID
library(plyr)
tree_plot <- join(tree,plt_cond,type='left',by=c('PLT_CN','CONDID'))  # put tree, plot, and condition info together
write.csv(tree_plot,row.names=F,file=sprintf('~/ufrc_hpc/FIA_1.6.1_20180110/%s_TREE_PLOT.csv',state))
