from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions  import date_format, to_date,col
import glob
import h5py
from datetime import datetime
import numpy as np
import sys

timestamp = datetime.now().strftime("%m%d_%H%M")
print('timestamp: ' + str(timestamp))
files = glob.glob('/n/hernquistfs3/IllustrisTNG/Runs/L75n455TNG/output/subbox1/snapdir_subbox1*/*.hdf5')
print(len(files))
def extract_parent_info(filepath):
    dat = h5py.File(filepath, mode='r')
    tracers = np.array([])
    ptype = 'PartType3'
    if (ptype not in dat.keys()):
        return []

    return np.array(dat['PartType3']['ParentID'])

def read_file(filepath):
    try:
        ret = extract_parent_info(filepath)
        return ret
    except Exception as ex:
        print(ex)
        return []

conf = SparkConf().setAppName('GenerateTracerParent')
sc = SparkContext(conf = conf)

df = sc.parallelize(files)
df.flatMap(read_file)           \
    .map(lambda x: (x,1))       \
    .reduceByKey(lambda x,y: x) \
    .map(lambda x: x[0])        \
    .saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))
