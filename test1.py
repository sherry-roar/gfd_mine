import time
import timeout_decorator
import urllib

@timeout_decorator.timeout(6)
def mytest(x):
    print("Start")
    for i in range(1,10):
        time.sleep(1)
        print("No.%a :" %x ,"{} seconds have passed".format(i))

def url_parse(url):
    url = urllib.parse.urlparse(url).path

    if url.rfind('/') == (len(url) - 1):
        url = url[:-1]

    head = url.find('/')
    end = url.rfind('/')
    datetype = url[head + 1:end]
    data = url[end + 1:]
    return data

def gen_query(p,mode=0):
    """

    :param p:三元组
    :param e:边e
    :return: 符合查询格式的查询
    """
    entity1 = []
    entity2 = []
    entity = []
    result = ''
    temp1 = []
    if mode==0:
        if isinstance(p[0], list):
            for p1 in p:
                temp1, entity2 = gen_query(p1)
                # temp1 is fixed pattern
                result = result + temp1
                for i in entity2:
                    if i not in entity1:
                        entity1.append(i)
        else:
            for _ in [0, 2]:
                temp2 = '<' + p[_] + '> '
                entity1.append(temp2)
                # temp2 is entities
            p1 = url_parse(p[0])
            p2 = url_parse(p[2])
            s1 = '?' + p1 + ' a <' + str(p[0]) + '>.'
            e1 = '?' + p2 + ' a <' + str(p[2]) + '>.'
            p1 = '?' + p1 + ' <' + str(p[1]) + '> ?' + p2 + '.'
            result = s1 + e1 + p1
        for i in entity1:
            if i not in entity:
                entity.append(i)
        # print(result)
        return result, entity
    elif mode==1:
        if isinstance(p[0], list):
            for p1 in p:
                entity2 = gen_query(p1,mode=1)
                for i in entity2:
                    if i not in entity1:
                        entity1.append(i)
        else:
            for _ in [0, 2]:
                temp2 = p[_]
                entity1.append(temp2)
        for i in entity1:
            if i not in entity:
                entity.append(i)
            # print(result)
        return entity

def labeling(lab):
    if len(lab)==3 and len(lab[0])==1:
        result=[['a',lab[1],'b']]
    else:
        result=[['a',lab[0][1],'b']]
        ind=ord('b')
        result1=[lab[0]]
        for t in lab[1:]:
            for temp in result1:
                if t[0] in temp:
                    if t[0]==temp[0]:
                        temp1=result[result1.index(temp)][0]
                        result.append([temp1,t[1],chr(ind+1)])
                        ind+=1
                    else:
                        temp1=result[result1.index(temp)][2]
                        result.append([temp1, t[1], chr(ind + 1)])
                        ind += 1
    return result

if __name__ == '__main__':
    a=[['x','e1','y'],['y','e2','z'],['y','e3','z2']]
    # b,c=gen_query(a)
    # print(b,'\n',c)
    print(labeling(a))