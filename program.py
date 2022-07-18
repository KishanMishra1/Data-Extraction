import ast
import csv
import json
import pandas as pd
from  collections import *


def findminmaxval(col):
    min_col_x = float('inf')
    max_col_x = float('-inf')
    for i in col:
        min_col_x = min(min_col_x, i[0])
        max_col_x = max(max_col_x, i[2])
    return [min_col_x, max_col_x]

def extract_data(coordinates,labels,mappedVal,rowcolwisedata,csv_file=False,json_file=False):
    res = dict()
    sorted_val = []
    rex = sorted(coordinates, key=lambda x: x[0])
    for i in range(len(rex)):
        sorted_ = {
            'bbox': rex[i],
            'originalIndex': coordinates.index(rex[i]),
            'label': labels[coordinates.index(rex[i])],
            'textValue': mappedVal[coordinates.index(rex[i])]
        }
        sorted_val.append(sorted_)
    # Converted row bbox mapping from the output
    rowbboxmaps = dict()
    for line in rowcolwisedata:
        k = []
        res = ast.literal_eval(str(line))
        if res['row'] in rowbboxmaps:
            rowbboxmaps[res['row']].append(res['bbox'])
        else:
            rowbboxmaps[res['row']] = [res['bbox']]
    #print(rowbboxmaps)

    #Sorted the row bbox mapping w.r.t x cordinates
    sorted_rowbboxmaps=dict()
    for i,j in rowbboxmaps.items():
        j=sorted(j,key=lambda x:x[0])
        sorted_rowbboxmaps[i]=j
    #print(sorted_rowbboxmaps)

    # Corresponding textvalues for every bbox for reference
    k=sorted_val
    bbox=[]
    textvalue=[]
    for i in k:
        bbox.append(i['bbox'])
        textvalue.append(i['textValue'])
    #print(bbox) [[30.9086, 158.5487, 296.6993, 179.8233], [32.3923, 190.0922, 45.2024, 204.593], ...
    #print(textvalue) ['S. Description BATCH EXP Qty Amt ', '1 ', '3 ', '5 ', ..
    rowtextvaluemaps=dict()
    for i,j in sorted_rowbboxmaps.items():
        temp=[]
        for k in j:
            k=textvalue[bbox.index(k)]
            temp.append(k)
        rowtextvaluemaps[i]=temp
    #print(rowtextvaluemaps) {0: ['S. ', 'Description ', 'BATCH ', 'EXP ', 'Qty ', 'Amt '], 1: ['1 ', 'DERMAZOLE 200 CAP ', ..
    values=list(rowtextvaluemaps.values())

    #Calculating Maximum columns in the matrix
    maxcol=0
    col=[]
    for i in values:
        maxcol=max(maxcol,len(i))
    #print("maxcol -->",maxcol)

    # Finding min x1 and max x2 of every column
    j,k=0,0
    res=dict()
    minmaxmat=[]
    while(j<maxcol):
        col=[]
        for i in values:
            col.append(bbox[textvalue.index(i[j])])
            m=findminmaxval(col)
        res={
            'column':j,
            'min x1':m[0],
            'max x2':m[1]
        }
        minmaxmat.append(res)
        j+=1
    #print(minmaxmat) [{'column': 0, 'min x1': 32.3923, 'max x2': 49.1715}, {'column': 1, 'min x1': 45.7815, 'max x2': 138.8433},..

    # Finding coordinates between min x1 and max x2
    final=[]
    for i in range(len(values)):
        ans=[]
        for j in range(maxcol):
            if j==minmaxmat[j]['column']:
                rng=sorted_rowbboxmaps.get(i)
                #print(rng)
                for itr in rng:
                    count=0
                    if minmaxmat[j]['min x1']<= itr[0] and itr[2]<=minmaxmat[j]['max x2']:
                        count+=1
                        ans.append(textvalue[bbox.index(itr)])
                        rng.remove(itr)
                        break
                    else:
                        ans.append('NaN')
                        break
        final.append(ans)
    # Cellwise matrix
    #print(final)

    #Updated Dataframe
    new_data = values[1:]

    df = pd.DataFrame(new_data, columns=values[0])
    if csv_file==True:
        df.to_csv('receipts_data.csv',index=False,header=True)

    #print(df)  Printing updated dataframe

    mapped_data={}
    #Predefined classes
    indexes=['S','S.','Sl.','SlNo.','Index','index','Sr.No.','Sr.','Serial No.','Sl.No.']
    Items=['Description','Item Name','Items','Particulars','Item']
    Batch=['BATCH','Group','Batch']
    expiry_date=['EXP','Expiry','Exp.Date','Expiry Date']
    Quantity=['Qty','Quantity']
    Pack=['Pack']
    Discount=['Dis Amt','Discount Price','Discount']
    Amount=['Price','Retail Price','Amt','Amount','Total','Total Amount']

    x=(df.columns.tolist())
    for i in x:
        if i.strip() in indexes:
            mapped_data["Item_Numbers"]=df[i].tolist()
        elif i.strip() in Items:
            mapped_data["Item_Names"]=df[i].tolist()
        elif i.strip() in Batch:
            mapped_data["Item_Batches"]=df[i].tolist()
        elif i.strip() in expiry_date:
            mapped_data["Item_Expiry_Dates"]=df[i].tolist()
        elif i.strip() in Quantity:
            mapped_data["Item_Quantitys"]=df[i].tolist()
        elif i.strip() in Pack:
            mapped_data["Items_Packs"]=df[i].tolist()
        elif i.strip() in Discount:
            mapped_data['Item_Discounts']=df[i].tolist()
        elif i.strip() in Amount:
            mapped_data['Item_Totalamounts'] = df[i].tolist()
    if json_file==True:
        with open("receipts_data.json", "w") as outfile:
            json.dump(mapped_data, outfile, indent=4, sort_keys=False)
    return mapped_data



if __name__=="__main__":
    coordinates = [[34.7824, 159.3622, 293.1888, 299.9614],
                   [34.6722, 234.3953, 297.4153, 250.6666],
                   [173.8602, 280.0276, 198.4157, 293.7276],
                   [172.7401, 206.0832, 197.7644, 219.7695],
                   [172.4045, 264.7139, 197.8062, 278.8651],
                   [47.4822, 280.3400, 104.3263, 293.7280],
                   [172.4984, 190.1835, 198.4245, 204.4720],
                   [34.4901, 249.3851, 299.0981, 265.7386],
                   [172.3175, 250.1150, 198.5759, 264.5946],
                   [267.4330, 160.0964, 294.8381, 175.0770],
                   [240.7606, 280.3613, 262.3429, 295.1627],
                   [263.0791, 207.3753, 295.8922, 221.2283],
                   [36.1252, 220.3776, 298.6593, 235.8702],
                   [261.4391, 191.1072, 294.7290, 205.6038],
                   [46.2775, 206.1816, 131.4995, 219.8094],
                   [213.2465, 159.8378, 238.3824, 175.5257],
                   [48.0051, 160.5074, 105.4748, 175.3474],
                   [240.0662, 191.2226, 261.7707, 205.8844],
                   [45.7815, 190.2173, 131.9277, 204.0477],
                   [172.9288, 234.9676, 194.3816, 250.0904],
                   [32.3923, 190.0922, 45.2024, 204.5930],
                   [32.6523, 205.8668, 302.8129, 220.3890],
                   [262.4793, 236.2009, 295.6144, 250.7398],
                   [213.1859, 250.2987, 236.7193, 264.3104],
                   [213.6835, 279.8993, 235.7227, 293.6695],
                   [172.3413, 220.9971, 200.0812, 235.1362],
                   [213.2312, 206.2410, 235.4198, 220.0546],
                   [213.9772, 265.3637, 235.2937, 278.4290],
                   [33.5923, 264.8986, 300.7874, 279.0065],
                   [45.9005, 250.2058, 112.9267, 263.7183],
                   [261.8689, 251.2414, 295.3882, 265.9702],
                   [213.1739, 190.4260, 236.2887, 204.3601],
                   [32.9577, 205.4763, 45.2708, 219.9568],
                   [213.7211, 235.3345, 235.5704, 249.8194],
                   [240.1659, 159.5372, 263.8281, 176.3875],
                   [248.8130, 251.5945, 260.8691, 265.4070],
                   [248.2767, 207.2500, 261.4125, 220.7070],
                   [47.4781, 264.7031, 138.8433, 278.8613],
                   [265.6289, 280.4766, 295.3783, 295.6590],
                   [270.4088, 221.3242, 295.9179, 236.0294],
                   [213.7760, 220.7912, 235.3564, 234.2048],
                   [248.9246, 266.1225, 260.7475, 279.7746],
                   [262.5620, 265.9505, 295.3616, 280.4076],
                   [248.3996, 221.8442, 261.7839, 235.7724],
                   [33.3481, 189.4106, 298.6230, 204.9713],
                   [35.0781, 160.3643, 49.1715, 174.1171],
                   [32.7153, 235.1718, 45.0486, 249.1042],
                   [47.5424, 221.1727, 123.3136, 234.6945],
                   [30.9086, 158.5487, 296.6993, 179.8233],
                   [248.6716, 236.6241, 261.1073, 250.5159],
                   [32.8026, 279.1273, 45.3481, 293.1983],
                   [173.2634, 159.8922, 210.5613, 174.9239],
                   [32.7156, 265.6530, 44.7885, 278.1850],
                   [32.5747, 250.2187, 45.5170, 264.3090],
                   [32.4870, 220.9806, 45.2071, 234.4210],
                   [47.5893, 235.7042, 118.8901, 248.9414],
                   [36.7806, 279.2197, 286.2352, 295.2628]]
    labels = [0, 2, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3,
              3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3,
              1, 3, 3, 3, 3, 3, 3, 3, 2]
    mappedVal = {
        0: 'S. Description 1 DERMAZOLE 200 CAP 2 KENACORT 40MG INJ 3 DISPOVAN SYRING 4 FUNGIZOLE SOAP 5 LUVATE CREAM 6 FUNGIZOLE SOLUTION 7 WELZIN 5 TAB BATCH EXP Qty Amt 0132 0378 4SR1 596 0223 0241 130A 8/23 2 : 0 198.00 9/24 1 154.50 1/27 1 6.50 8/23 1 145.00 8/23 1 230.00 3/23 1 165.00 7123 1 : 0 25.00 ',
        1: '4 FUNGIZOLE SOAP 596 8/23 1 145.00 ', 2: '130A ', 3: '0378 ', 4: '0241 ', 5: 'WELZIN 5 TAB ', 6: '0132 ',
        7: '5 LUVATE CREAM 0223 8/23 1 230.00 ', 8: '0223 ', 9: 'Amt ', 10: '1 : 0 ', 11: '154.50 ',
        12: '3 DISPOVAN SYRING 4SR1 1/27 1 6.50 ', 13: '198.00 ', 14: 'KENACORT 40MG INJ ', 15: 'EXP ',
        16: 'Description ', 17: '2 : 0 ', 18: 'DERMAZOLE 200 CAP ', 19: '596 ', 20: '1 ',
        21: '2 KENACORT 40MG INJ 0378 9/24 1 154.50 ', 22: '145.00 ', 23: '8/23 ', 24: '7123 ', 25: '4SR1 ',
        26: '9/24 ', 27: '3/23 ', 28: '6 FUNGIZOLE SOLUTION 0241 3/23 1 165.00 ', 29: 'LUVATE CREAM ', 30: '230.00 ',
        31: '8/23 ', 32: '2 ', 33: '8/23 ', 34: 'Qty ', 35: '1 ', 36: '1 ', 37: 'FUNGIZOLE SOLUTION ', 38: '25.00 ',
        39: '6.50 ', 40: '1/27 ', 41: '1 ', 42: '165.00 ', 43: '1 ', 44: '1 DERMAZOLE 200 CAP 0132 8/23 2 : 0 198.00 ',
        45: 'S. ', 46: '4 ', 47: 'DISPOVAN SYRING ', 48: 'S. Description BATCH EXP Qty Amt ', 49: '1 ', 50: '7 ',
        51: 'BATCH ', 52: '6 ', 53: '5 ', 54: '3 ', 55: 'FUNGIZOLE SOAP ', 56: '7 WELZIN 5 TAB 130A 7123 1 : 0 25.00 '}

    rowcolwisedata = [{'col': 3, 'row': 0, 'bbox': [240.1659, 159.5372, 263.8281, 176.3875]},
                      {'col': 2, 'row': 0, 'bbox': [213.2465, 159.8378, 238.3824, 175.5257]},
                      {'col': 1, 'row': 0, 'bbox': [173.2634, 159.8922, 210.5613, 174.9239]},
                      {'col': 5, 'row': 0, 'bbox': [267.433, 160.0964, 294.8381, 175.077]},
                      {'col': 0, 'row': 0, 'bbox': [35.0781, 160.3643, 49.1715, 174.1171]},
                      {'col': 0, 'row': 0, 'bbox': [48.0051, 160.5074, 105.4748, 175.3474]},
                      {'col': 0, 'row': 1, 'bbox': [32.3923, 190.0922, 45.2024, 204.593]},
                      {'col': 1, 'row': 1, 'bbox': [172.4984, 190.1835, 198.4245, 204.472]},
                      {'col': 0, 'row': 1, 'bbox': [45.7815, 190.2173, 131.9277, 204.0477]},
                      {'col': 2, 'row': 1, 'bbox': [213.1739, 190.426, 236.2887, 204.3601]},
                      {'col': 4, 'row': 1, 'bbox': [261.4391, 191.1072, 294.729, 205.6038]},
                      {'col': 3, 'row': 1, 'bbox': [240.0662, 191.2226, 261.7707, 205.8844]},
                      {'col': 0, 'row': 2, 'bbox': [32.9577, 205.4763, 45.2708, 219.9568]},
                      {'col': 1, 'row': 2, 'bbox': [172.7401, 206.0832, 197.7644, 219.7695]},
                      {'col': 0, 'row': 2, 'bbox': [46.2775, 206.1816, 131.4995, 219.8094]},
                      {'col': 2, 'row': 2, 'bbox': [213.2312, 206.241, 235.4198, 220.0546]},
                      {'col': 3, 'row': 2, 'bbox': [248.2767, 207.25, 261.4125, 220.707]},
                      {'col': 4, 'row': 2, 'bbox': [263.0791, 207.3753, 295.8922, 221.2283]},
                      {'col': 2, 'row': 3, 'bbox': [213.776, 220.7912, 235.3564, 234.2048]},
                      {'col': 0, 'row': 3, 'bbox': [32.487, 220.9806, 45.2071, 234.421]},
                      {'col': 1, 'row': 3, 'bbox': [172.3413, 220.9971, 200.0812, 235.1362]},
                      {'col': 0, 'row': 3, 'bbox': [47.5424, 221.1727, 123.3136, 234.6945]},
                      {'col': 5, 'row': 3, 'bbox': [270.4088, 221.3242, 295.9179, 236.0294]},
                      {'col': 3, 'row': 3, 'bbox': [248.3996, 221.8442, 261.7839, 235.7724]},
                      {'col': 1, 'row': 4, 'bbox': [172.9288, 234.9676, 194.3816, 250.0904]},
                      {'col': 0, 'row': 4, 'bbox': [32.7153, 235.1718, 45.0486, 249.1042]},
                      {'col': 2, 'row': 4, 'bbox': [213.7211, 235.3345, 235.5704, 249.8194]},
                      {'col': 0, 'row': 4, 'bbox': [47.5893, 235.7042, 118.8901, 248.9414]},
                      {'col': 4, 'row': 4, 'bbox': [262.4793, 236.2009, 295.6144, 250.7398]},
                      {'col': 3, 'row': 4, 'bbox': [248.6716, 236.6241, 261.1073, 250.5159]},
                      {'col': 1, 'row': 5, 'bbox': [172.3175, 250.115, 198.5759, 264.5946]},
                      {'col': 0, 'row': 5, 'bbox': [45.9005, 250.2058, 112.9267, 263.7183]},
                      {'col': 0, 'row': 5, 'bbox': [32.5747, 250.2187, 45.517, 264.309]},
                      {'col': 2, 'row': 5, 'bbox': [213.1859, 250.2987, 236.7193, 264.3104]},
                      {'col': 4, 'row': 5, 'bbox': [261.8689, 251.2414, 295.3882, 265.9702]},
                      {'col': 3, 'row': 5, 'bbox': [248.813, 251.5945, 260.8691, 265.407]},
                      {'col': 0, 'row': 6, 'bbox': [47.4781, 264.7031, 138.8433, 278.8613]},
                      {'col': 1, 'row': 6, 'bbox': [172.4045, 264.7139, 197.8062, 278.8651]},
                      {'col': 2, 'row': 6, 'bbox': [213.9772, 265.3637, 235.2937, 278.429]},
                      {'col': 0, 'row': 6, 'bbox': [32.7156, 265.653, 44.7885, 278.185]},
                      {'col': 4, 'row': 6, 'bbox': [262.562, 265.9505, 295.3616, 280.4076]},
                      {'col': 3, 'row': 6, 'bbox': [248.9246, 266.1225, 260.7475, 279.7746]},
                      {'col': 0, 'row': 7, 'bbox': [32.8026, 279.1273, 45.3481, 293.1983]},
                      {'col': 2, 'row': 7, 'bbox': [213.6835, 279.8993, 235.7227, 293.6695]},
                      {'col': 1, 'row': 7, 'bbox': [173.8602, 280.0276, 198.4157, 293.7276]},
                      {'col': 0, 'row': 7, 'bbox': [47.4822, 280.34, 104.3263, 293.728]},
                      {'col': 3, 'row': 7, 'bbox': [240.7606, 280.3613, 262.3429, 295.1627]},
                      {'col': 5, 'row': 7, 'bbox': [265.6289, 280.4766, 295.3783, 295.659]}]

    print(extract_data(coordinates,labels,mappedVal,rowcolwisedata,csv_file=False,json_file=False))
    # set csv_file True to download csv file of the table
    # set json_file True to download json file of mapped data