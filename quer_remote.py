from SPARQLWrapper import SPARQLWrapper, JSON
import urllib
import timeout_decorator
import time

DBpedia_endpoint = "http://localhost:8890/sparql"

@timeout_decorator.timeout(1)
def DBpedia_query1(_query, kb_endpoint, q_type=0):
    """

    :param _query: sparql query statement
    :param kb_endpoint:
    :param q_type:0 is SELECT,1 is ASK,2 is DISCRIBE
    :return:
    """
    sparql = SPARQLWrapper(kb_endpoint)
    sparql.setQuery(_query)
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()
    # print(response)
    if q_type==0:
        _,result = parse_query_result(response,_query)
    elif q_type==1:
        result=response['boolean']
    return result

def DBpedia_query(_query, kb_endpoint, q_type=0):
    """

    :param _query: sparql query statement
    :param kb_endpoint:
    :param q_type:0 is SELECT,1 is ASK,2 is DISCRIBE
    :return:
    """
    sparql = SPARQLWrapper(kb_endpoint)
    sparql.setQuery(_query)
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()
    # print(response)
    if q_type==0:
        _,result = parse_query_result(response,_query)
    elif q_type==1:
        result=response['boolean']
    return result

def parse_query_result(response, value):
    """

    :param response: dict type result
    :param value: value we want from dict
    :return:
    """
    list1 = response['results']['bindings']
    key = []
    list2 = []
    if list1:
        for _ in list1[0].keys():
            key.append(_)
        l = len(key)
        list2 = [[] for _ in range(l)]
        for i in range(len(list1)):
            ind = 0
            for v in list1[i].values():
                list2[ind].append(v['value'])
                ind += 1
    # print("list2:",list2)
    return key, list2

def url_parse(url):
    url = urllib.parse.urlparse(url).path

    if url.rfind('/') == (len(url) - 1):
        url = url[:-1]

    head = url.find('/')
    end = url.rfind('/')
    datetype = url[head + 1:end]
    data = url[end + 1:]
    return data

def gen_query(p):
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

def labeling(lab):
    if len(lab)==3 and len(lab[0])>3:
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

def count(pattern, structure=[],mode=1):
    """
    count this pattern
    :param pattern:
    :param mode:0 is count graph structure,1 is count pattern
    :return:
    """
    '''
    pattern[0]->RHS
    pattern[1]->LHS
    '''
    if mode==1:
        if len(pattern) == 3:
            s = pattern[0]
            o = pattern[2]
            p = pattern[1]
            quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                        ?s a <''' + s + '''>.
                        ?o a <''' + o + '''>.
                        ?s <''' + p + '''> ?o.
                        }'''

        elif len(pattern) == 2:
            if len(pattern[1])==2:
                if len(structure)==3:
                    if structure[0][0] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                       FROM<http://dbpedia-2016.org>{
                                       ?s <''' + p1 + '''> ?o.
                                       ?s <''' + p2 + '''> ?o2.
                                       ?s <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] ==structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                            quc = quc1 + quc2

                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                                  FROM<http://dbpedia-2016.org>{
                                                                  ?s <''' + p1 + '''> ?o.
                                                                  ?s <''' + p2 + '''> ?o2.
                                                                  ?o <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''

                            quc = quc1 + quc2

                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                                  FROM<http://dbpedia-2016.org>{
                                                                  ?s <''' + p1 + '''> ?o.
                                                                  ?s <''' + p2 + '''> ?o2.
                                                                  ?o2 <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''

                            quc = quc1 + quc2

                    elif structure[0][2] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                       FROM<http://dbpedia-2016.org>{
                                       ?s <''' + p1 + '''> ?o.
                                       ?o <''' + p2 + '''> ?o2.
                                       ?s <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                            quc = quc1 + quc2

                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                                  FROM<http://dbpedia-2016.org>{
                                                                  ?s <''' + p1 + '''> ?o.
                                                                  ?o <''' + p2 + '''> ?o2.
                                                                  ?o <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''

                            quc = quc1 + quc2

                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                                  FROM<http://dbpedia-2016.org>{
                                                                  ?s <''' + p1 + '''> ?o.
                                                                  ?o <''' + p2 + '''> ?o2.
                                                                  ?o2 <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o2 a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?s a <''' + pattern[1][0] + '''>.
                                                                              ?o3 a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?s a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                              ?o3 a <''' + pattern[1][0] + '''>.
                                                                              ?o a <''' + pattern[1][1] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?o2 a <''' + pattern[1][0] + '''>.
                                                                             ?s a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o2 a <''' + pattern[1][1] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                             ?s a <''' + pattern[1][0] + '''>.
                                                                             ?o a <''' + pattern[1][1] + '''>.}'''

                            quc = quc1 + quc2

                else:
                    if structure[0][0] == structure[1][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        quc1 = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                                    ?s <''' + p1 + '''> ?o.
                                                                    ?s <''' + p2 + '''> ?o2.
                                                                   '''
                        if pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1][0] + '''>.
                                            ?o2 a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1][0] + '''>.
                                            ?s a <''' + pattern[1][1] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][0]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1][0] + '''>.
                                            ?o a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1][0] + '''>.
                                            ?s a <''' + pattern[1][1] + '''>.}'''
                        elif pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1][0] + '''>.
                                            ?o2 a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1][0] + '''>.
                                            ?o a <''' + pattern[1][1] + '''>.}'''
                        else:
                            quc2 = '}'
                        quc = quc1 + quc2

                    elif structure[0][2] == structure[1][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        quc1 = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                       '''
                        if pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1][0] + '''>.
                                            ?o2 a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1][0] + '''>.
                                            ?s a <''' + pattern[1][1] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][0]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1][0] + '''>.
                                            ?o a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1][0] + '''>.
                                            ?s a <''' + pattern[1][1] + '''>.}'''
                        elif pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1][0] + '''>.
                                            ?o2 a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1][0] + '''>.
                                            ?o a <''' + pattern[1][1] + '''>.}'''
                        else:
                            quc2 = '}'
                        quc = quc1 + quc2

            elif len(pattern[1]) == 3:
                if structure[0][0] == structure[1][0]:
                    if structure[2][0] == structure[0][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                   FROM<http://dbpedia-2016.org>{
                                   ?s <''' + p1 + '''> ?o.
                                   ?s <''' + p2 + '''> ?o2.
                                   ?s <''' + p3 + '''> ?o3.'''
                        if pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''

                        else:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        quc = quc1 + quc2

                    elif structure[2][0] == structure[0][2]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                      FROM<http://dbpedia-2016.org>{
                                      ?s <''' + p1 + '''> ?o.
                                      ?s <''' + p2 + '''> ?o2.
                                      ?o <''' + p3 + '''> ?o3.'''
                        if pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                        else:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                        quc = quc1 + quc2

                    else:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                      FROM<http://dbpedia-2016.org>{
                                      ?s <''' + p1 + '''> ?o.
                                      ?s <''' + p2 + '''> ?o2.
                                      ?o2 <''' + p3 + '''> ?o3.'''
                        if pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                        else:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                        quc = quc1 + quc2

                elif structure[0][2] == structure[1][0]:
                    if structure[2][0] == structure[0][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                   FROM<http://dbpedia-2016.org>{
                                   ?s <''' + p1 + '''> ?o.
                                   ?o <''' + p2 + '''> ?o2.
                                   ?s <''' + p3 + '''> ?o3.'''
                        if pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o2 a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o2 a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?s a <''' + pattern[1][0] + '''>.
                                               ?o3 a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?s a <''' + pattern[1][1] + '''>.
                                               ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                               ?o3 a <''' + pattern[1][0] + '''>.
                                               ?o a <''' + pattern[1][1] + '''>.
                                               ?s a <''' + pattern[1][2] + '''>.}'''

                        else:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        quc = quc1 + quc2

                    elif structure[2][0] == structure[0][2]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                      FROM<http://dbpedia-2016.org>{
                                      ?s <''' + p1 + '''> ?o.
                                      ?o <''' + p2 + '''> ?o2.
                                      ?o <''' + p3 + '''> ?o3.'''
                        if pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                        else:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                        quc = quc1 + quc2

                    else:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                      FROM<http://dbpedia-2016.org>{
                                      ?s <''' + p1 + '''> ?o.
                                      ?o <''' + p2 + '''> ?o2.
                                      ?o2 <''' + p3 + '''> ?o3.'''
                        if pattern[0] == structure[0][0]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[0][2]:
                            if pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o2 a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o2 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o2 a <''' + pattern[1][2] + '''>.}'''

                        elif pattern[0] == structure[1][2]:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[0][0]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?o3 a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?s a <''' + pattern[1][0] + '''>.
                                              ?o3 a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?s a <''' + pattern[1][1] + '''>.
                                              ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                              ?o3 a <''' + pattern[1][0] + '''>.
                                              ?o a <''' + pattern[1][1] + '''>.
                                              ?s a <''' + pattern[1][2] + '''>.}'''

                        else:
                            if pattern[1][0] == structure[0][2]:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[1][0] == structure[1][2]:
                                if pattern[1][1] == structure[1][0]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?s a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1][0] + '''>.
                                             ?s a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o2 a <''' + pattern[1][1] + '''>.
                                             ?o a <''' + pattern[1][2] + '''>.}'''
                                else:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1][0] + '''>.
                                             ?o a <''' + pattern[1][1] + '''>.
                                             ?o2 a <''' + pattern[1][2] + '''>.}'''

                        quc = quc1 + quc2

            else:
                if len(structure) == 2:
                    if structure[0][0] == structure[1][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        quc1 = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                                    ?s <''' + p1 + '''> ?o.
                                                                    ?s <''' + p2 + '''> ?o2.
                                                                   '''
                        if pattern[0]==structure[0][2]:
                            if pattern[1] == structure[0][0]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            if pattern[1] == structure[0][0]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1] + '''>.}'''
                        elif pattern[0] == structure[0][0]:
                            if pattern[1] == structure[0][2]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1] + '''>.}'''
                        else:
                            quc2 = '}'
                        quc=quc1+quc2

                    elif structure[0][2] == structure[1][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        quc1 = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                       '''
                        if pattern[0] == structure[0][2]:
                            if pattern[1] == structure[0][0]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            if pattern[1] == structure[0][0]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1] + '''>.}'''
                        elif pattern[0] == structure[0][0]:
                            if pattern[1] == structure[0][2]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1] + '''>.}'''
                        else:
                            quc2 = '}'
                        quc = quc1 + quc2

                elif len(structure) == 3 and len(structure[0]) == 3:
                    if structure[0][0] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                    FROM<http://dbpedia-2016.org>{
                                    ?s <''' + p1 + '''> ?o.
                                    ?s <''' + p2 + '''> ?o2.
                                    ?s <''' + p3 + '''> ?o3.
                                                                        '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <'''+ pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            else:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2
                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                            FROM<http://dbpedia-2016.org>{
                                                            ?s <''' + p1 + '''> ?o.
                                                            ?s <''' + p2 + '''> ?o2.
                                                            ?o <''' + p3 + '''> ?o3.
                                                                                   '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            else:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2
                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                            FROM<http://dbpedia-2016.org>{
                                                            ?s <''' + p1 + '''> ?o.
                                                            ?s <''' + p2 + '''> ?o2.
                                                            ?o2 <''' + p3 + '''> ?o3.
                                                                                     '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            else:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2

                    elif structure[0][2] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                    FROM<http://dbpedia-2016.org>{
                                    ?s <''' + p1 + '''> ?o.
                                    ?o <''' + p2 + '''> ?o2.
                                    ?s <''' + p3 + '''> ?o3.
                                                                        '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            else:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2
                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                        FROM<http://dbpedia-2016.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                        ?o <''' + p3 + '''> ?o3.
                                                                                   '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            else:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2
                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                        FROM<http://dbpedia-2016.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                        ?o2 <''' + p3 + '''> ?o3.
                                                                                     '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            else:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                             ?o2 a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                             ?o3 a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2

                else:
                    if pattern[0]==structure[2]:
                        o = pattern[0]
                        s = pattern[1]
                        p = structure[1]
                        quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                ?s a <''' + s + '''>.
                                                ?o a <''' + o + '''>.
                                                ?s <''' + p + '''> ?o.
                                                }'''
                    else:
                        s = pattern[0]
                        o = pattern[1]
                        p = structure[1]
                        quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                ?s a <''' + s + '''>.
                                                ?o a <''' + o + '''>.
                                                ?s <''' + p + '''> ?o.
                                                }'''

        elif len(pattern) == 1:
            if len(structure)==2:
                if structure[0][0] == structure[1][0]:
                    p1 = structure[0][1]
                    p2 = structure[1][1]
                    quc1 = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?s <''' + p2 + '''> ?o2.
                                            '''
                    if pattern[0]==structure[0][0]:
                        quc2 = '''?s a <'''+ pattern[0] +'''>.}'''
                    elif pattern[0]==structure[0][2]:
                        quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                    elif pattern[0] == structure[1][2]:
                        quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                    else:
                        quc2 = '}'
                    quc=quc1+quc2
                elif structure[0][2] == structure[1][0]:
                    p1 = structure[0][1]
                    p2 = structure[1][1]
                    quc1 = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                            ?s <''' + p1 + '''> ?o.
                                                            ?o <''' + p2 + '''> ?o2.
                                                            '''
                    if pattern[0]==structure[0][0]:
                        quc2 = '''?s a <'''+ pattern[0] +'''>.}'''
                    elif pattern[0]==structure[0][2]:
                        quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                    elif pattern[0] == structure[1][2]:
                        quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                    else:
                        quc2 = '}'
                    quc=quc1+quc2

            elif len(structure)==1:
                o = pattern[0]
                p = structure[1]
                quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{

                                                        ?s <''' + p + '''> ?o.
                                                        ?o a <''' + o + '''>.
                                                        }'''

            elif len(structure) == 3 and len(structure[0]) == 3:
                if structure[0][0] == structure[1][0]:
                    if structure[2][0] == structure[0][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                FROM<http://dbpedia-2016.org>{
                                ?s <''' + p1 + '''> ?o.
                                ?s <''' + p2 + '''> ?o2.
                                ?s <''' + p3 + '''> ?o3.
                                                                    '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                        quc = quc1 + quc2
                    elif structure[2][0] == structure[0][2]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                                        FROM<http://dbpedia-2016.org>{
                                                        ?s <''' + p1 + '''> ?o.
                                                        ?s <''' + p2 + '''> ?o2.
                                                        ?o <''' + p3 + '''> ?o3.
                                                                               '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                        quc = quc1 + quc2
                    else:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                                        FROM<http://dbpedia-2016.org>{
                                                        ?s <''' + p1 + '''> ?o.
                                                        ?s <''' + p2 + '''> ?o2.
                                                        ?o2 <''' + p3 + '''> ?o3.
                                                                                 '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                        quc = quc1 + quc2

                elif structure[0][2] == structure[1][0]:
                    if structure[2][0] == structure[0][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                FROM<http://dbpedia-2016.org>{
                                ?s <''' + p1 + '''> ?o.
                                ?o <''' + p2 + '''> ?o2.
                                ?s <''' + p3 + '''> ?o3.
                                                                    '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                        quc = quc1 + quc2
                    elif structure[2][0] == structure[0][2]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                    FROM<http://dbpedia-2016.org>{
                                    ?s <''' + p1 + '''> ?o.
                                    ?o <''' + p2 + '''> ?o2.
                                    ?o <''' + p3 + '''> ?o3.
                                                                               '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                        quc = quc1 + quc2
                    else:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        p3 = structure[2][1]
                        quc1 = '''    select count distinct  * 
                                    FROM<http://dbpedia-2016.org>{
                                    ?s <''' + p1 + '''> ?o.
                                    ?o <''' + p2 + '''> ?o2.
                                    ?o2 <''' + p3 + '''> ?o3.
                                                                                 '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                        quc = quc1 + quc2

            else:
                if pattern[0]==structure[0]:
                    o = pattern[0]
                    p = structure[1]
                    quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                            ?s a <''' + o + '''>.
                                            ?s <''' + p + '''> ?o.
                                            }'''
                else:
                    o = pattern[0]
                    p = structure[1]
                    quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                                ?o a <''' + o + '''>.
                                                                ?s <''' + p + '''> ?o.
                                                                }'''

        else:
            p = structure[1]
            quc = '''    select count distinct  ?o FROM<http://dbpedia-2016.org>{
                                            ?o a <''' + pattern + '''>.
                                            ?s <''' + p + '''> ?o.
                                            }'''

    elif mode==0:
        if len(pattern)==2:
            if pattern[0][0]==pattern[1][0]:
                p1 = pattern[0][1]
                p2 = pattern[1][1]
                quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?s <''' + p2 + '''> ?o2.
                                        }'''
            elif pattern[0][2]==pattern[1][0]:
                p1 = pattern[0][1]
                p2 = pattern[1][1]
                quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                                        ?s <''' + p1 + '''> ?o.
                                                        ?o <''' + p2 + '''> ?o2.
                                                        }'''
        elif len(pattern)==1:
            p = pattern[1]
            quc = '''    select count distinct  * FROM<http://dbpedia-2016.org>{
                                    ?s <''' + p + '''> ?o.
                                    }'''
    # print(quc)
    jishu = DBpedia_query(quc, DBpedia_endpoint)[0][0]
    return int(jishu)

def gfdverifier(RHS, LHS, suma,p):
    """
    compute if gfd is frequent and not redundant
    supp就是gfd满足这个图模式下的所有条目中gfd的这个条目占的比例
    conf置信度就是LHS满足的条件下，RHS满足这个gfd的占比
    :param entity:
    :param ty:
    :return:
    """
    ind = 0
    if LHS is None:
        supp = count(RHS,structure=p) # 计算满足
        print('supp', supp)
        if supp > 150:
            ind = 1
    else:
        supp = count([RHS, LHS],structure=p) # 计算满足
        print('supp', supp)
        if supp > 150:
            ind = 1

    return ind

def gfdverifier1(RHS, LHS, suma,p):
    """
    compute if gfd is frequent and not redundant
    supp就是gfd满足这个图模式下的所有条目中gfd的这个条目占的比例
    conf置信度就是LHS满足的条件下，RHS满足这个gfd的占比
    :param entity:
    :param ty:
    :return:
    """
    ind = 0
    if LHS is None:
        supp = count(RHS,structure=p) / suma  # 计算满足
        print('supp', supp)
        if supp > 0.05:
            ind = 1
    else:
        if len(LHS)==2:
            ind=1
        else:
            supp = count([RHS, LHS],structure=p) / suma  # 计算满足
            print('supp', supp)
            if supp > 0.05:
                ind = 1

    return ind

class gfd_updater:
    """
    GFD updater
    """

    def __init__(self, Q=[], k=3, gfd=[[], []]):
        self.old_Q = Q
        self.new_Q = [[] for _ in range(k + 1)]
        self.Q = [[] for _ in range(k + 1)]
        self.delete_Q = []
        self.old_l = gfd
        print(self.old_l)
        self.new_l = [[[] for _ in range(4)] for _ in range(4)]
        # self.l = [[[] for _ in range(4)] for _ in range(4)]
        self.l = [[],[],[]]
        self.edge = []
        self.V_t = {'Q': self.Q, 'l': self.l}
        self.new_Q_init()

    def new_Q_init(self):
        """
        init new Q[0]
        :return:
        """
        qut = '''
            select  distinct ?p FROM<http://dbpedia-latest.org>{ 
            ?p rdfs:subClassOf* owl:Thing . 
            FILTER (REGEX(str(?p), "ontology", "i"))  
            }
            '''
        qt = DBpedia_query(qut, DBpedia_endpoint)[0]
        # print("qt =", qt)
        for t in qt:
            qtt = '''
                select count distinct ?p FROM<http://dbpedia-latest.org> { 
                ?p a <''' + t + '''> . 
                }
                '''
            tt = DBpedia_query(qtt, DBpedia_endpoint)[0][0]
            # print("tt =",tt)
            if int(tt) > 1000:
                # print(t, 'is added, sum is', tt)
                # 1000 is minial support
                self.Q[0].append(t)
        que = '''
            SELECT  DISTINCT ?prop 
            FROM<http://dbpedia-latest.org>
            WHERE {
              ?prop a rdf:Property 
            }
            '''
        self.edge = DBpedia_query(que, DBpedia_endpoint)[0]

    def stream_manager(self):
        for temp_Q in self.Q[0]:
            if temp_Q not in self.old_Q[0]:
                self.new_Q[0].append(temp_Q)
                # Q is to be generate new GFD
        for temp_Q in self.old_Q[0]:
            if temp_Q not in self.Q[0]:
                self.delete_Q.append(temp_Q)
                # delete_Q is going to be delete from GFDs
        print('delete',self.delete_Q,'\n add',self.new_Q)

    def new_vspawn(self):
        ind = 0
        for pattern in self.new_Q[0]:
            for e in self.edge:
                if ind >= 2000:
                    # raise ("1000 over")
                    break
                q1 = '''    select  distinct  ?o FROM<http://dbpedia-latest.org>{
                ?p a <''' + pattern + '''>.
                ?p <''' + e + '''> ?o.
                FILTER (!isLiteral(?o)). 
                 }'''
                try:
                    b = DBpedia_query1(q1, DBpedia_endpoint)
                except:
                    b=[]
                    print("ERROR b1",ind)
                if b:
                    if len(b[0]) > 150:
                        # print('query count : ',q1)
                        # print('count :', b[0])
                        for temp in b[0]:
                            q2 = '''    select  distinct  ?p2 FROM<http://dbpedia-latest.org>{
                            <''' + temp + '''> a ?p2.
                            ?p2 rdfs:subClassOf* owl:Thing.
                            FILTER(!REGEX(str(?p2), owl:Thing, "i"))
                            }'''
                            try:
                                p2 = DBpedia_query1(q2, DBpedia_endpoint)
                            except:
                                p2=[]
                                print('ERROR b2',ind)
                            if p2:
                                for _ in p2[0]:
                                    temp1 = [pattern, e, _]
                                    # print(temp,temp1)
                                    if temp1 not in self.new_Q[1]:
                                        self.new_Q[1].append(temp1)
                                        # print('Pattern ',ind,temp1,' added')
                                        ind = ind + 1

        ind = 0
        for pattern in self.new_Q[1]:
            # i=3
            for e in self.edge:
                if ind >= 1000:
                    break
                query = [[], []]
                head = "select count distinct ?p FROM<http://dbpedia-latest.org>{"
                head1 = "select distinct ?p FROM<http://dbpedia-latest.org>{"
                end1 = "?p rdfs:subClassOf* owl:Thing.?o a ?p."
                end2 = '?p a ?'
                end = ' <' + e + '> ?o.FILTER(!REGEX(str(?p), owl:Thing, "i"))}'
                query[0], quentity = gen_query(pattern)
                for _ in quentity:
                    query[1] = '?' + url_parse(_)[:-2]
                    q = head1 + query[0] + end1 + query[1] + end
                    # print(q)
                    try:
                        b = DBpedia_query1(q, DBpedia_endpoint)
                    except:
                        print("b TIMEOUT: ", q)
                        b = []
                    if b:
                        for o in b[0]:
                            q2 = head + query[0] + '?p a <' + o + '>.' + query[1] + ' <' + e + '> ?p.}'
                            try:
                                b2 = DBpedia_query1(q2, DBpedia_endpoint)[0][0]
                            except:
                                print("b2 TIMEOUT: ", q2)
                                b2 = 0
                            if int(b2) >= 15:
                                # print("No %a time count is %a!"%(ind,b2))
                                if [_[1:-2], e, o] != pattern and [pattern, [_[1:-2], e, o]] \
                                        not in self.new_Q[2]:
                                    self.new_Q[2].append([pattern, [_[1:-2], e, o]])
                                    ind += 1
                                    # print('No.%a '%ind ,b2, [pattern, [_[1:-2], e, o]])

        ind = 0
        for pattern in self.new_Q[2]:
            # i=3
            for e in edge:
                if ind >= 1000:
                    break
                query = [[], []]
                head = "select count distinct ?p FROM<http://dbpedia-latest.org>{"
                head1 = "select distinct ?p FROM<http://dbpedia-latest.org>{"
                end1 = "?p rdfs:subClassOf* owl:Thing.?o a ?p."
                end2 = '?p a ?'
                end = ' <' + e + '> ?o.FILTER(!REGEX(str(?p), owl:Thing, "i"))}'
                query[0], quentity = gen_query(pattern)
                for _ in quentity:
                    query[1] = '?' + url_parse(_)[:-2]
                    q = head1 + query[0] + end1 + query[1] + end
                    # print(q)
                    try:
                        b = DBpedia_query1(q, DBpedia_endpoint)
                    except:
                        print("Q3 b TIMEOUT: ", q)
                        b = []
                    if b:
                        for o in b[0]:
                            q2 = head + query[0] + '?p a <' + o + '>.' + query[1] + ' <' + e + '> ?p.}'
                            # print(q2)
                            try:
                                b2 = DBpedia_query1(q2, DBpedia_endpoint)[0][0]
                            except:
                                print(" Q3 b2 TIMEOUT: ", q2)
                                b2 = 0
                            if int(b2) >= 15:
                                # print("No %a time count is %a!" % (ind, b2))
                                if [_[1:-2], e, o] != pattern[1] \
                                        and [_[1:-2], e, o] != pattern[0] and \
                                        [pattern[0], pattern[1], [_[1:-2], e, o]] \
                                        not in self.new_Q[3]:
                                    self.new_Q[3].append([pattern[0], pattern[1], [_[1:-2], e, o]])
                                    ind += 1
                                    # print('No.%a ' % ind, b2, [pattern[0], pattern[1], [_[1:-2], e, o]])
        print('\n', self.new_Q, '\n')

    def new_hspawn(self):
        ############################## self.l[0] #############################

        ################### 0
        self.l[0] = [[], []]
        self.l[0][0] = []
        # j=0
        RHS = LHS = []
        print('\n', '#' * 100, ' START Q1', '#' * 100)
        for pattern in self.new_Q[1]:
            # lo = Q[1].index(pattern)
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = LHS = []
                RHS.append(entity[1:-2])
                # print(RHS)
                # print(entity)
                LHS = None
                print('\nADD dep: [', LHS, '--->', RHS, ']')
                inde = self.gfdverifier(RHS, LHS, suma, p=pattern)
                if inde and [LHS, RHS[0], labeling(pattern)] not in self.l[0][0]:
                    self.l[0][0].append([LHS, RHS[0], labeling(pattern)])
                    # l[0][1].append(RHS)
                    # # Notice! need to find subclass
                    # l[0][0].append(LHS)
                    print('[', LHS, '--->', RHS, ']', 'Added complete!')
            print('-' * 200)
        print('#' * 100, ' Q1 OVER', len(self.l[0][0]), '#' * 100, '\n')
        print("Level 1: l0:", len(self.l[0][0]), "l1:", len(self.l[0][1]), "\nQ:", len(self.new_Q[1]))
        for _ in self.l[0][0][:15]: print(_, '\n')
        ###################### 1
        self.l[0][1] = []
        # j=1
        print('\n', '#' * 100, ' START Q2', '#' * 100)
        for pattern in self.new_Q[1]:
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个graph的个数
            print('pattern sum = ', suma)
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = []
                LHS = []
                RHS.append(entity[1:-2])
                # print('RHS', RHS)
                for entity1 in entities:
                    LHS = []
                    if entity1[1:-2] != RHS[0]:
                        LHS.append(entity1[1:-2])
                        print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                        if LHS:
                            inde = self.gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                            # print(inde,'\n')
                            if inde:
                                temp2 = []
                                for temp2 in self.l[0][1]:
                                    q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                            {
                                            <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                            }'''
                                    q_ask_L = '''ask FROM<http://dbpedia-latest.org>
                                            {
                                            <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                            }'''
                                    if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                            or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                        inde = 0
                                        print(temp2, 'CANNOT ADD!!')
                                        break
                                if inde and [LHS[0], RHS[0], labeling(pattern)] not in self.l[0][1]:
                                    temp2 = []
                                    for temp2 in self.l[0][1]:
                                        q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                }'''
                                        q_ask_L = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                                }'''
                                        if temp2[2][0] == labeling(pattern) and \
                                                (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                                 or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                            self.l[0][1].remove(temp2)
                                            print(temp2, 'REMOVED!!!')
                                    self.l[0][1].append([LHS[0], RHS[0], labeling(pattern)])
                                    print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                    ##########def reducedgfd():
                                    temp2 = []
                                    for temp2 in self.l[0][0]:  # remove redundant gfd in l0
                                        if temp2[2][0] == labeling(pattern) \
                                                and temp2[1] == RHS[0]:
                                            self.l[0][0].remove(temp2)
                                            print(temp2, 'REMOVED!!!')
        print('#' * 100, ' Q2 OVER', len(self.l[0][1]), '#' * 100, '\n')
        print("Level1 : l0:", len(self.l[0][0]), "l1:", len(self.l[0][1]), "\nQ:", len(self.Q[1]))
        for _ in self.l[0][1][:15]: print(_, '\n')

        ######################## self.l[1] ############################
        self.l[1] = [[], [], []]
        ######################## 0
        self.l[1][0] = []
        # j=0
        RHS = LHS = []
        print('\n', '#' * 100, ' START Q1', '#' * 100)
        for pattern in self.new_Q[2]:
            # lo = Q[1].index(pattern)
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = LHS = []
                RHS.append(entity[1:-2])
                # print(RHS)
                # print(entity)
                LHS = None
                print('\nADD dep: [', LHS, '--->', RHS, ']')
                inde = self.gfdverifier(RHS, LHS, suma, p=pattern)
                if inde and [LHS, RHS[0], labeling(pattern)] not in l2[0]:
                    l2[0].append([LHS, RHS[0], labeling(pattern)])
                    # l[0][1].append(RHS)
                    # # Notice! need to find subclass
                    # l[0][0].append(LHS)
                    print('[', LHS, '--->', RHS, ']', 'Added complete!')
            print('-' * 200)

        print('#' * 100, ' Q1 OVER', len(self.l[1][0]), '#' * 100, '\n')
        print("Level 2:  l0:", len(self.l[1][0]), "l1:", len(self.l[1][1]),
              "l2:", len(self.l[1][2]), "\nQ:", len(self.Q[2]))
        for _ in self.l[1][0][:15]: print(_, '\n')
        ###################### 1
        self.l[1][1] = []
        # j=1
        print('\n', '#' * 100, ' START Q2', '#' * 100)
        for pattern in self.new_Q[2]:
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个graph的个数
            # print('pattern sum = ', suma)
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = []
                LHS = []
                RHS.append(entity[1:-2])
                # print('RHS', RHS)
                for entity1 in entities:
                    LHS = []
                    if entity1[1:-2] != RHS[0]:
                        LHS.append(entity1[1:-2])
                        print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                        if LHS:
                            inde = self.gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                            # print(inde,'\n')
                            if inde:
                                temp2 = []
                                for temp2 in self.l[1][1]:
                                    q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                                }'''
                                    q_ask_L = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                                }'''
                                    if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                            or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                        inde = 0
                                        print(temp2, 'CANNOT ADD!!')
                                        break
                                if inde and [LHS[0], RHS[0], labeling(pattern)] not in self.l[1][1]:
                                    temp2 = []
                                    for temp2 in self.l[1][1]:
                                        q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                    }'''
                                        q_ask_L = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                                    }'''
                                        if (temp2[2] == labeling(pattern)) and \
                                                (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                                 or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                            self.l[1][1].remove(temp2)
                                            print(temp2, 'REMOVED!!!')
                                    self.l[1][1].append([LHS[0], RHS[0], labeling(pattern)])
                                    print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                    ##########def reducedgfd():
                                    temp2 = []
                                    for temp2 in self.l[1][0]:  # remove redundant gfd in l0
                                        if (temp2[2] == labeling(pattern)) \
                                                and temp2[1] == RHS[0]:
                                            self.l[1][1].remove(temp2)
                                            print(temp2, 'REMOVED!!!')

        print('#' * 100, ' Q2 OVER', len(self.l[1][1]), '#' * 100, '\n')
        print("Level 2:  l0:", len(self.l[1][0]), "l1:", len(self.l[1][1]),
              "l2:", len(self.l[1][2]), "\nQ:", len(self.Q[2]))
        for _ in self.l[1][1][:15]: print(_, '\n')
        #################### 2
        self.l[1][2] = []
        print('\n', '#' * 100, ' START Q3', '#' * 100)
        for pattern in self.new_Q[2]:
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个graph的个数
            # print('pattern sum = ', suma)
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = []
                LHS = []
                RHS.append(entity[1:-2])
                # print('RHS', RHS)
                for entity1 in entities:
                    if entity1[1:-2] != RHS[0]:
                        LHS.append(entity1[1:-2])
                # LHS=[[],[]],RHS=[]
                if LHS and len(LHS) > 1:
                    print('\nADD dep: [', LHS, '--->', RHS, ']')
                    inde = self.gfdverifier(RHS[0], LHS, suma, p=pattern)
                    # print(inde,'\n')
                    if inde:
                        temp2 = []
                        for temp2 in self.l[1][2]:
                            q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                        {
                                        <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                        }'''
                            q_ask_L1 = '''ask FROM<http://dbpedia-latest.org>
                                        {
                                        <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                        }'''
                            q_ask_L2 = '''ask FROM<http://dbpedia-latest.org>
                                        {
                                        <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                        }'''
                            if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                    or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                    DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1):
                                inde = 0
                                print(temp2, 'CANNOT ADD!!')
                                break
                        if inde and [LHS, RHS[0], labeling(pattern)] not in self.l[1][2]:
                            temp2 = []
                            for temp2 in self.l[1][2]:
                                q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                            {
                                            <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                            }'''
                                q_ask_L1 = '''ask FROM<http://dbpedia-latest.org>
                                            {
                                            <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                            }'''
                                q_ask_L2 = '''ask FROM<http://dbpedia-latest.org>
                                            {
                                            <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                            }'''
                                if temp2[2] == labeling(pattern) and \
                                        (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                         or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                         DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
                                    self.l[1][2].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            self.l[1][2].append([LHS, RHS[0], labeling(pattern)])
                            print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                            ##########def reducedgfd():
                            temp2 = []
                            for temp2 in self.l[1][1]:  # remove redundant gfd in l0
                                if temp2[2] == labeling(pattern) \
                                        and temp2[1] == RHS[0] and temp2[0] in LHS:
                                    self.l[1][1].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            temp2 = []
                            for temp2 in self.l[1][0]:  # remove redundant gfd in l0
                                if (temp2[2] == labeling(pattern)) \
                                        and temp2[1] == RHS[0]:
                                    self.l[1][0].remove(temp2)
                                    print(temp2, 'REMOVED!!!')

        print('#' * 100, ' Q3 OVER', len(self.l[1][2]), '#' * 100, '\n')
        print("Level 2:  l0:", len(self.l[1][0]), "l1:", len(self.l[1][1]),
              "l2:", len(self.l[1][2]), "\nQ:", len(self.Q[2]))
        for _ in self.l[1][2][:15]: print(_, '\n')

        ###################### self.l[2] ###############################
        self.l[2] = [[], [], [], []]
        ###################### 0
        self.l[2][0] = []
        # j=0
        RHS = LHS = []
        print('\n', '#' * 100, ' START Q1', '#' * 100)
        for pattern in self.new_Q[3]:
            # lo = Q[1].index(pattern)
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = LHS = []
                RHS.append(entity[1:-2])
                # print(RHS)
                # print(entity)
                LHS = None
                print('\nADD dep: [', LHS, '--->', RHS, ']')
                inde = self.gfdverifier(RHS, LHS, suma, p=pattern)
                if inde and [LHS, RHS[0], labeling(pattern)] not in self.l[2][0]:
                    self.l[2][0].append([LHS, RHS[0], labeling(pattern)])
                    # l[0][1].append(RHS)
                    # # Notice! need to find subclass
                    # l[0][0].append(LHS)
                    print('[', LHS, '--->', RHS, ']', 'Added complete!')
            print('-' * 200)

        print('#' * 100, ' Q1 OVER', len(self.l[2][0]), '#' * 100, '\n')
        print("Level 3:  l0:", len(self.l[2][0]), "l1:", len(self.l[2][1]),
              "l2:", len(self.l[2][2]), "l3:", len(self.l[2][3]), "\nQ:", len(self.Q[3]))
        for _ in self.l[2][0][:15]: print(_, '\n')
        ###################### 1
        self.l[2][1] = []
        # j=1
        print('\n', '#' * 100, ' START Q2', '#' * 100)
        for pattern in self.new_Q[3]:
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个graph的个数
            # print('pattern sum = ', suma)
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = []
                LHS = []
                RHS.append(entity[1:-2])
                # print('RHS', RHS)
                for entity1 in entities:
                    LHS = []
                    if entity1[1:-2] != RHS[0]:
                        LHS.append(entity1[1:-2])
                        print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                        if LHS:
                            inde = self.gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                            # print(inde,'\n')
                            if inde:
                                temp2 = []
                                for temp2 in self.l[2][1]:
                                    q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                                    }'''
                                    q_ask_L = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                                    }'''
                                    if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                            or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                        inde = 0
                                        print(temp2, 'CANNOT ADD!!')
                                        break
                                if inde and [LHS[0], RHS[0], labeling(pattern)] not in self.l[2][1]:
                                    temp2 = []
                                    for temp2 in self.l[2][1]:
                                        q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                        {
                                                        <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                        }'''
                                        q_ask_L = '''ask FROM<http://dbpedia-latest.org>
                                                        {
                                                        <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                                        }'''
                                        if (temp2[2] == labeling(pattern)) and \
                                                (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                                 or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                            self.l[2][1].remove(temp2)
                                            print(temp2, 'REMOVED!!!')
                                    self.l[2][1].append([LHS[0], RHS[0], labeling(pattern)])
                                    print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                    ##########def reducedgfd():
                                    temp2 = []
                                    for temp2 in self.l[2][0]:  # remove redundant gfd in l0
                                        if (temp2[2] == labeling(pattern)) \
                                                and temp2[1] == RHS[0]:
                                            self.l[2][0].remove(temp2)
                                            print(temp2, 'REMOVED!!!')

        print('#' * 100, ' Q2 OVER', len(self.l[2][1]), '#' * 100, '\n')
        print("Level 3:  l0:", len(self.l[2][0]), "l1:", len(self.l[2][1]),
              "l2:", len(self.l[2][2]), "l3:", len(self.l[2][3]), "\nQ:", len(self.Q[3]))
        for _ in self.l[2][1][:15]: print(_, '\n')
        ################ 2
        self.l[2][2] = []
        print('\n', '#' * 100, ' START Q3', '#' * 100)
        for pattern in self.new_Q[3]:
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个graph的个数
            # print('pattern sum = ', suma)
            _, entities = gen_query(pattern)
            for entity in entities:
                entities_cp = entities[:]
                entities_cp.remove(entity)
                RHS = []
                LHS = []
                LHS_list = []
                temp2 = []
                RHS.append(entity[1:-2])
                # print('RHS', RHS)
                for i in range(len(entities_cp))[:-1]:
                    for j in range(len(entities_cp))[1:]:
                        if j > i:
                            temp2.append(entities_cp[i][1:-2])
                            temp2.append(entities_cp[j][1:-2])
                            LHS_list.append(temp2)
                            temp2 = []
                for LHS in LHS_list:
                    # LHS=[[],[]],RHS=[]
                    if LHS and len(LHS) == 2:
                        print('\nADD dep: [', LHS, '--->', RHS, ']')
                        inde = self.gfdverifier(RHS[0], LHS, suma, p=pattern)
                        # print(inde,'\n')
                        if inde:
                            temp2 = []
                            for temp2 in self.l[2][2]:
                                q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                                }'''
                                q_ask_L1 = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                                }'''
                                q_ask_L2 = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                                }'''
                                if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                        or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                        DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1):
                                    inde = 0
                                    print(temp2, 'CANNOT ADD!!')
                                    break
                            if inde and [LHS, RHS[0], labeling(pattern)] not in self.l[2][2]:
                                temp2 = []
                                for temp2 in self.l[2][2]:
                                    q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                    }'''
                                    q_ask_L1 = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                                    }'''
                                    q_ask_L2 = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                                    }'''
                                    if temp2[2] == labeling(pattern) and \
                                            (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                             or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                             DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
                                        self.l[2][2].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
                                self.l[2][2].append([LHS, RHS[0], labeling(pattern)])
                                print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                ##########def reducedgfd():
                                temp2 = []
                                for temp2 in self.l[2][1]:  # remove redundant gfd in l0
                                    if temp2[2] == labeling(pattern) \
                                            and temp2[1] == RHS[0] and temp2[0] in LHS:
                                        self.l[2][1].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
                                temp2 = []
                                for temp2 in self.l[2][0]:  # remove redundant gfd in l0
                                    if (temp2[2] == labeling(pattern)) \
                                            and temp2[1] == RHS[0]:
                                        self.l[2][0].remove(temp2)
                                        print(temp2, 'REMOVED!!!')

        print('#' * 100, ' Q3 OVER', len(self.l[2][2]), '#' * 100, '\n')
        print("Level 3:  l0:", len(self.l[2][0]), "l1:", len(self.l[2][1]),
              "l2:", len(self.l[2][2]), "l3:", len(self.l[2][3]), "\nQ:", len(self.Q[3]))
        for _ in self.l[2][2][:15]: print(_, '\n')
        #################### 3
        self.l[2][3] = []
        print('\n', '#' * 100, ' START Q4', '#' * 100)
        for pattern in self.new_Q[3]:
            print('\n', '-' * 200)
            print(pattern)
            RHS = LHS = []
            suma = 1  # 计算满足这个graph的个数
            # print('pattern sum = ', suma)
            _, entities = gen_query(pattern)
            for entity in entities:
                RHS = []
                LHS = []
                RHS.append(entity[1:-2])
                # print('RHS', RHS)
                for entity1 in entities:
                    if entity1[1:-2] != RHS[0]:
                        LHS.append(entity1[1:-2])
                # LHS=[[],[]],RHS=[]
                if LHS and len(LHS) == 3:
                    print('\nADD dep: [', LHS, '--->', RHS, ']')
                    inde = self.gfdverifier(RHS[0], LHS, suma, p=pattern)
                    # print(inde,'\n')
                    if inde:
                        temp2 = []
                        for temp2 in self.l[2][3]:
                            q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                                }'''
                            q_ask_L1 = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                                }'''
                            q_ask_L2 = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                                }'''
                            q_ask_L3 = '''ask FROM<http://dbpedia-latest.org>
                                                {
                                                <''' + temp2[0][2] + '''> rdfs:subClassOf <''' + LHS[2] + '''>.
                                                }'''
                            if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                    or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                    DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1) or \
                                    DBpedia_query(q_ask_L3, DBpedia_endpoint, q_type=1):
                                inde = 0
                                print(temp2, 'CANNOT ADD!!')
                                break
                        if inde and [LHS, RHS[0], labeling(pattern)] not in self.l[2][3]:
                            temp2 = []
                            for temp2 in self.l[2][3]:
                                q_ask_R = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                    }'''
                                q_ask_L1 = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                                    }'''
                                q_ask_L2 = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                                    }'''
                                q_ask_L3 = '''ask FROM<http://dbpedia-latest.org>
                                                    {
                                                    <''' + LHS[2] + '''> rdfs:subClassOf <''' + temp2[0][2] + '''>.
                                                    }'''
                                if temp2[2] == labeling(pattern) and \
                                        (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                         or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                         DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1) or \
                                         DBpedia_query(q_ask_L3, DBpedia_endpoint, q_type=1)):
                                    self.l[2][3].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            self.l[2][3].append([LHS, RHS[0], labeling(pattern)])
                            print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                            ##########def reducedgfd():
                            temp2 = []
                            for temp2 in self.l[2][2]:  # remove redundant gfd in l0
                                if temp2[2] == labeling(pattern) \
                                        and temp2[1] == RHS[0] and (temp2[0][0] in LHS) \
                                        and (temp2[0][1] in LHS):
                                    self.l[2][2].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            temp2 = []
                            for temp2 in self.l[2][1]:  # remove redundant gfd in l0
                                if temp2[2] == labeling(pattern) \
                                        and temp2[1] == RHS[0] and (temp2[0] in LHS):
                                    self.l[2][1].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            temp = []
                            for temp2 in self.l[2][0]:  # remove redundant gfd in l0
                                if (temp2[2] == labeling(pattern)) \
                                        and temp2[1] == RHS[0]:
                                    self.l[2][0].remove(temp2)
                                    print(temp2, 'REMOVED!!!')

        print('#' * 100, ' Q4 OVER', len(self.l[2][3]), '#' * 100, '\n')
        print("Level 3:  l0:", len(self.l[2][0]), "l1:", len(self.l[2][1]),
              "l2:", len(self.l[2][2]), "l3:", len(self.l[2][3]), "\nQ:", len(self.Q[3]))
        for _ in self.l[2][3][:15]: print(_, '\n')

    def new_vspawn1(self, i):
        """
        纵向扩展生成树
        会查到重复的pattern例如[[a,b,c][d,e,f]]和[[d,e,f][a,b,c]]
        :param i: level i
        :return:
        """
        ind = 0
        if i == 1:
            for pattern in self.new_Q[0]:
                for e in self.edge:
                    if ind >= 100:
                        # raise ("1000 over")
                        break
                    q1 = '''    select  distinct  ?o FROM<http://dbpedia-latest.org>{
                                        ?p a <''' + pattern + '''>.
                                        ?p <''' + e + '''> ?o.
                                        FILTER (!isLiteral(?o)). 

                                         }'''
                    b = DBpedia_query(q1, DBpedia_endpoint)
                    if b:
                        if len(b[0]) > 15:
                            # print('query count : ',q1)
                            # print('count :', b[0])
                            for temp in b[0]:
                                q2 = '''    select  distinct  ?p2 FROM<http://dbpedia-latest.org>{
                                                    <''' + temp + '''> a ?p2.
                                                    ?p2 rdfs:subClassOf* owl:Thing.
                                                    FILTER(!REGEX(str(?p2), owl:Thing, "i"))
                                                    }'''
                                p2 = DBpedia_query(q2, DBpedia_endpoint)
                                if p2:
                                    for _ in p2[0]:
                                        temp1 = [pattern, e, _]
                                        # print(temp,temp1)
                                        if temp1 not in self.Q[1]:
                                            self.new_Q[1].append(temp1)
                                            # print('Pattern ',ind,temp1,' added')
                                            ind = ind + 1
        elif i == 2:
            ind = 0
            for pattern in self.new_Q[1]:
                # i=3
                for e in self.edge:
                    if ind >= 100:
                        break
                    query = [[], []]
                    head = "select count distinct ?p FROM<http://dbpedia-latest.org>{"
                    head1 = "select distinct ?p FROM<http://dbpedia-latest.org>{"
                    end1 = "?p rdfs:subClassOf* owl:Thing.?o a ?p."
                    end2 = '?p a ?'
                    end = ' <' + e + '> ?o.FILTER(!REGEX(str(?p), owl:Thing, "i"))}'
                    query[0], quentity = gen_query(pattern)
                    for _ in quentity:
                        query[1] = '?' + url_parse(_)[:-2]
                        q = head1 + query[0] + end1 + query[1] + end
                        # print(q)
                        try:
                            b = DBpedia_query1(q, DBpedia_endpoint)
                        except:
                            print("b TIMEOUT: ", q)
                            b = []
                        if b:
                            for o in b[0]:
                                q2 = head + query[0] + '?p a <' + o + '>.' + query[1] + ' <' + e + '> ?p.}'
                                try:
                                    b2 = DBpedia_query1(q2, DBpedia_endpoint)[0][0]
                                except:
                                    print("b2 TIMEOUT: ", q2)
                                    b2 = 0
                                if int(b2) >= 1:
                                    print("No %a time count is %a!" % (ind, b2))
                                    if [_[1:-2], e, o] != pattern and [pattern, [_[1:-2], e, o]] not in self.Q[2]:
                                        self.new_Q[2].append([pattern, [_[1:-2], e, o]])
                                        ind += 1
                                        print('No.%a ' % ind, b2, [pattern, [_[1:-2], e, o]])
        elif i == 3:
            []
        else:
            for pattern in self.Q[i - 1]:
                # i=3
                for e in self.edge:
                    query = [[], []]
                    head = "select count distinct ?p FROM<http://dbpedia-latest.org>{"
                    head1 = "select distinct ?p FROM<http://dbpedia-latest.org>{"
                    end = ' <' + e + "> ?o." \
                                     "?p rdfs:subClassOf* owl:Thing." \
                                     "?o a ?p}"
                    query[0], quentity = gen_query(pattern)
                    for _ in quentity:
                        query[1] = '?' + url_parse(_)
                        q = head + query[0] + query[1] + end
                        # print(q)
                        b = DBpedia_query(q, DBpedia_endpoint)[1][0]
                        if int(b[0]) >= 100:
                            q = head1 + query[0] + query[1] + end
                            # print(q)
                            b = DBpedia_query(q, DBpedia_endpoint)[1][0]
                            if b:
                                for _1 in b[0]:
                                    if isinstance(pattern[0], list):
                                        temp = list(pattern)
                                        temp.append([_[1:-2], e, _1])
                                        if [_[1:-2], e, _1] not in pattern and temp not in self.Q[i]:
                                            self.Q[i].append(temp)
                                    else:
                                        temp = [pattern, [_[1:-2], e, _1]]
                                        if [_[1:-2], e, _1] != pattern and temp not in self.Q[i]:
                                            self.Q[i].append(temp)

    def new_hspawn1(self, i, j):
        """
        generate dependencies of level-i,in j where j range from [0,i]
        :param i: level-i
        :param j:
        :return: no return, verified dependencies are added to self.l
        """
        self.new_l[i][j] = []
        # the 2 list are LHS and RHS respectively
        RHS = LHS = []
        print('\n', '#' * 100, ' START Q1', '#' * 100)
        for pattern in self.new_Q[i]:
            RHS = LHS = []
            print('\n', '-' * 200)
            print(pattern)
            suma = self.count(pattern, mode=0)  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            if j == 0:
                for entity in entities:

                    RHS.append(entity[1:-2])
                    LHS = None
                    print('\nADD dep: [', LHS, '--->', RHS, ']')
                    ind = self.gfdverifier(RHS, LHS, suma, p=pattern)
                    if ind and [LHS, RHS[0], [pattern[0][1], pattern[1][1]]] not in self.l[0]:
                        self.new_l[i][j].append([LHS, RHS[0], [pattern[0][1], pattern[1][1]]])
                        # Notice! need to find subclass
                        print('[', LHS, '--->', RHS, ']', 'Added complete!')
            elif j == i + 4:
                for entity in entities:
                    RHS = entity[1:-2]
                    for entity1 in entities:
                        if entity1 != entity:
                            LHS.append(entity1[1:-2])
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.l[i][j][1].append(RHS)
                        self.l[i][j][0].append(LHS)
            elif j == 1:
                for entity in entities:
                    RHS = []
                    LHS = []
                    RHS.append(entity[1:-2])
                    # print('RHS', RHS)
                    for entity1 in entities:
                        LHS = []
                        if entity1[1:-2] != RHS[0]:
                            LHS.append(entity1[1:-2])
                            print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                            if LHS:
                                inde = self.gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                                # print(inde,'\n')
                                if inde:
                                    for temp2 in self.new_l[i][j]:
                                        q_ask_R = '''ask
                                                    {
                                                    <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                                    }'''
                                        q_ask_L = '''ask
                                                    {
                                                    <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                                    }'''
                                        if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                                or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                            inde = 0
                                            print(temp2, 'CANNOT ADD!!')
                                            break
                                    if inde and [LHS[0], RHS[0], [pattern[0][1], pattern[1][1]]] not in self.l[i][j]:
                                        # for temp2 in self.new_l[i][j]:
                                        #     q_ask_R = '''ask
                                        #                 {
                                        #                 <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                        #                 }'''
                                        #     q_ask_L = '''ask
                                        #                 {
                                        #                 <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                        #                 }'''
                                        #     if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] and \
                                        #             (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                        #              or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                        #         self.new_l[i][j].remove(temp2)
                                        #         print(temp2, 'REMOVED!!!')
                                        self.new_l[i][j].append([LHS[0], RHS[0], [pattern[0][1], pattern[1][1]]])
                                        print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                        ##########def reducedgfd():
                                        # for temp2 in self.l[0]:  # remove redundant gfd in l0
                                        #     if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] \
                                        #             and temp2[1] == RHS[0]:
                                        #         self.l[i][j - 1].remove(temp2)
                                        #         print(temp2, 'REMOVED!!!')
                # t_entity = self.bianli(entities, j)
                # for entity in t_entity:
                #     RHS = entity[1:-2]
                #     for entity1 in entities:
                #         if entity1 != entity:
                #             LHS.append(entity1[1:-2])
                #     ind = self.gfdverifier(RHS, LHS, suma)
                #     if ind:
                #         self.l[i][j][1].append(RHS)
                #         self.l[i][j][0].append(LHS)


            # for pattern in self.Q[2]:
            #     print('\n', '-' * 200)
            #     print(pattern)
            #     RHS = LHS = []
            #     suma = self.count(pattern, mode=0)  # 计算满足这个graph的个数
            #     print('pattern sum = ', suma)
            #     _, entities = gen_query(pattern)
            #     for entity in entities:
            #         RHS = []
            #         LHS = []
            #         RHS.append(entity[1:-2])
            #         # print('RHS', RHS)
            #         for entity1 in entities:
            #             LHS = []
            #             if entity1[1:-2] != RHS[0]:
            #                 LHS.append(entity1[1:-2])
            #                 print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
            #                 if LHS:
            #                     inde = self.gfdverifier(RHS[0], LHS[0], suma, p=pattern)
            #                     # print(inde,'\n')
            #                     if inde:
            #                         for temp2 in self.l[1]:
            #                             q_ask_R = '''ask
            #                             {
            #                             <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
            #                             }'''
            #                             q_ask_L = '''ask
            #                             {
            #                             <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
            #                             }'''
            #                             if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
            #                                     or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
            #                                 inde = 0
            #                                 print(temp2, 'CANNOT ADD!!')
            #                                 break
            #                         if inde and [LHS[0], RHS[0], [pattern[0][1], pattern[1][1]]] not in self.l[1]:
            #                             for temp2 in self.l[1]:
            #                                 q_ask_R = '''ask
            #                                 {
            #                                 <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
            #                                 }'''
            #                                 q_ask_L = '''ask
            #                                 {
            #                                 <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
            #                                 }'''
            #                                 if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] and \
            #                                         (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
            #                                          or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
            #                                     self.l[1].remove(temp2)
            #                                     print(temp2, 'REMOVED!!!')
            #                             self.l[1].append([LHS[0], RHS[0], [pattern[0][1], pattern[1][1]]])
            #                             print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
            #                             ##########def reducedgfd():
            #                             for temp2 in self.l[0]:  # remove redundant gfd in l0
            #                                 if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] \
            #                                         and temp2[1] == RHS[0]:
            #                                     self.l[0].remove(temp2)
            #                                     print(temp2, 'REMOVED!!!')
            elif j == 2:
                for entity in entities:
                    RHS = []
                    LHS = []
                    RHS.append(entity[1:-2])
                    # print('RHS', RHS)
                    for entity1 in entities:
                        if entity1[1:-2] != RHS[0]:
                            LHS.append(entity1[1:-2])
                    print('\nADD dep: [', LHS, '--->', RHS, ']')
                    # LHS=[[],[]],RHS=[]
                    if LHS and len(LHS) > 1:
                        inde = self.gfdverifier(RHS[0], LHS, suma, p=pattern)
                        # print(inde,'\n')
                        if inde:
                            for temp2 in self.new_l[i][j]:
                                q_ask_R = '''ask
                                                {
                                                <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                                }'''
                                q_ask_L1 = '''ask
                                                {
                                                <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                                }'''
                                q_ask_L2 = '''ask
                                                {
                                                <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                                }'''
                                if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                        or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                        DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1):
                                    inde = 0
                                    print(temp2, 'CANNOT ADD!!')
                                    break
                            if inde and [LHS, RHS[0], [pattern[0][1], pattern[1][1]]] not in self.new_l[i][j]:
                                # for temp2 in self.new_l[i][j]:
                                #     q_ask_R = '''ask
                                #                     {
                                #                     <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                #                     }'''
                                #     q_ask_L1 = '''ask
                                #                     {
                                #                     <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                #                     }'''
                                #     q_ask_L2 = '''ask
                                #                     {
                                #                     <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                #                     }'''
                                #     if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] and \
                                #             (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                #              or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                #              DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
                                #         self.l[i][j].remove(temp2)
                                #         print(temp2, 'REMOVED!!!')
                                self.new_l[i][j].append([LHS, RHS[0], [pattern[0][1], pattern[1][1]]])
                                print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                ##########def reducedgfd():
                                # for temp2 in self.l[i][j - 1]:  # remove redundant gfd in l0
                                #     if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] \
                                #             and temp2[1] == RHS[0] and temp2[0] in LHS:
                                #         self.l[i][j - 1].remove(temp2)
                                #         print(temp2, 'REMOVED!!!')

    def count(self, pattern, structure=[], mode=1):
        """
        count this pattern
        :param pattern:
        :param mode:0 is count graph structure,1 is count pattern
        :return:
        """
        '''
        pattern[0]->RHS
        pattern[1]->LHS
        '''
        if mode == 1:
            if len(pattern) == 3:
                s = pattern[0]
                o = pattern[2]
                p = pattern[1]
                quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                            ?s a <''' + s + '''>.
                            ?o a <''' + o + '''>.
                            ?s <''' + p + '''> ?o.
                            }'''

            elif len(pattern) == 2:
                if len(pattern[1]) == 2:
                    if len(structure) == 3:
                        if structure[0][0] == structure[1][0]:
                            if structure[2][0] == structure[0][0]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                           FROM<http://dbpedia-latest.org>{
                                           ?s <''' + p1 + '''> ?o.
                                           ?s <''' + p2 + '''> ?o2.
                                           ?s <''' + p3 + '''> ?o3.'''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[0][2]:
                                    if pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[1][2]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o a <''' + pattern[1][0] + '''>.
                                                      ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o a <''' + pattern[1][0] + '''>.
                                                      ?s a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o2 a <''' + pattern[1][0] + '''>.
                                                      ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o2 a <''' + pattern[1][0] + '''>.
                                                      ?s a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?s a <''' + pattern[1][0] + '''>.
                                                      ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?s a <''' + pattern[1][0] + '''>.
                                                      ?o a <''' + pattern[1][1] + '''>.}'''

                                quc = quc1 + quc2

                            elif structure[2][0] == structure[0][2]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                                                      FROM<http://dbpedia-latest.org>{
                                                                      ?s <''' + p1 + '''> ?o.
                                                                      ?s <''' + p2 + '''> ?o2.
                                                                      ?o <''' + p3 + '''> ?o3.'''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[0][2]:
                                    if pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[1][2]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''

                                quc = quc1 + quc2

                            else:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                                                      FROM<http://dbpedia-latest.org>{
                                                                      ?s <''' + p1 + '''> ?o.
                                                                      ?s <''' + p2 + '''> ?o2.
                                                                      ?o2 <''' + p3 + '''> ?o3.'''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[0][2]:
                                    if pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[1][2]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''

                                quc = quc1 + quc2

                        elif structure[0][2] == structure[1][0]:
                            if structure[2][0] == structure[0][0]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                           FROM<http://dbpedia-latest.org>{
                                           ?s <''' + p1 + '''> ?o.
                                           ?o <''' + p2 + '''> ?o2.
                                           ?s <''' + p3 + '''> ?o3.'''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[0][2]:
                                    if pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o2 a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[1][2]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?s a <''' + pattern[1][0] + '''>.
                                                       ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                       ?o3 a <''' + pattern[1][0] + '''>.
                                                       ?o a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o a <''' + pattern[1][0] + '''>.
                                                      ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o a <''' + pattern[1][0] + '''>.
                                                      ?s a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o2 a <''' + pattern[1][0] + '''>.
                                                      ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?o2 a <''' + pattern[1][0] + '''>.
                                                      ?s a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?s a <''' + pattern[1][0] + '''>.
                                                      ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                      ?s a <''' + pattern[1][0] + '''>.
                                                      ?o a <''' + pattern[1][1] + '''>.}'''

                                quc = quc1 + quc2

                            elif structure[2][0] == structure[0][2]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                                                      FROM<http://dbpedia-latest.org>{
                                                                      ?s <''' + p1 + '''> ?o.
                                                                      ?o <''' + p2 + '''> ?o2.
                                                                      ?o <''' + p3 + '''> ?o3.'''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[0][2]:
                                    if pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[1][2]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''

                                quc = quc1 + quc2

                            else:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                                                      FROM<http://dbpedia-latest.org>{
                                                                      ?s <''' + p1 + '''> ?o.
                                                                      ?o <''' + p2 + '''> ?o2.
                                                                      ?o2 <''' + p3 + '''> ?o3.'''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?s a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[0][2]:
                                    if pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''

                                elif pattern[0] == structure[1][2]:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[0][0]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?s a <''' + pattern[1][0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[0][0]:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?s a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                                                  ?o a <''' + pattern[1][1] + '''>.}'''

                                else:
                                    if pattern[1][0] == structure[0][2]:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    elif pattern[1][0] == structure[1][2]:
                                        if pattern[1][1] == structure[1][0]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                                                 ?s a <''' + pattern[1][1] + '''>.}'''

                                    else:
                                        if pattern[1][1] == structure[1][2]:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o2 a <''' + pattern[1][1] + '''>.}'''
                                        else:
                                            quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                                                 ?s a <''' + pattern[1][0] + '''>.
                                                                                 ?o a <''' + pattern[1][1] + '''>.}'''

                                quc = quc1 + quc2

                    else:
                        if structure[0][0] == structure[1][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                                        ?s <''' + p1 + '''> ?o.
                                                                        ?s <''' + p2 + '''> ?o2.
                                                                       '''
                            if pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1][0] + '''>.
                                                ?o2 a <''' + pattern[1][1] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1][0] + '''>.
                                                ?s a <''' + pattern[1][1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1][0] + '''>.
                                                ?o a <''' + pattern[1][1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1][0] + '''>.
                                                ?s a <''' + pattern[1][1] + '''>.}'''
                            elif pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1][0] + '''>.
                                                ?o2 a <''' + pattern[1][1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1][0] + '''>.
                                                ?o a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '}'
                            quc = quc1 + quc2

                        elif structure[0][2] == structure[1][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?o <''' + p2 + '''> ?o2.
                                           '''
                            if pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1][0] + '''>.
                                                ?o2 a <''' + pattern[1][1] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1][0] + '''>.
                                                ?s a <''' + pattern[1][1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1][0] + '''>.
                                                ?o a <''' + pattern[1][1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1][0] + '''>.
                                                ?s a <''' + pattern[1][1] + '''>.}'''
                            elif pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1][0] + '''>.
                                                ?o2 a <''' + pattern[1][1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1][0] + '''>.
                                                ?o a <''' + pattern[1][1] + '''>.}'''
                            else:
                                quc2 = '}'
                            quc = quc1 + quc2

                elif len(pattern[1]) == 3:
                    if structure[0][0] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                       FROM<http://dbpedia-latest.org>{
                                       ?s <''' + p1 + '''> ?o.
                                       ?s <''' + p2 + '''> ?o2.
                                       ?s <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            quc = quc1 + quc2

                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                          FROM<http://dbpedia-latest.org>{
                                          ?s <''' + p1 + '''> ?o.
                                          ?s <''' + p2 + '''> ?o2.
                                          ?o <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                            quc = quc1 + quc2

                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                          FROM<http://dbpedia-latest.org>{
                                          ?s <''' + p1 + '''> ?o.
                                          ?s <''' + p2 + '''> ?o2.
                                          ?o2 <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                            quc = quc1 + quc2

                    elif structure[0][2] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                       FROM<http://dbpedia-latest.org>{
                                       ?s <''' + p1 + '''> ?o.
                                       ?o <''' + p2 + '''> ?o2.
                                       ?s <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o2 a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o2 a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?s a <''' + pattern[1][0] + '''>.
                                                   ?o3 a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?s a <''' + pattern[1][1] + '''>.
                                                   ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                   ?o3 a <''' + pattern[1][0] + '''>.
                                                   ?o a <''' + pattern[1][1] + '''>.
                                                   ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            quc = quc1 + quc2

                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                          FROM<http://dbpedia-latest.org>{
                                          ?s <''' + p1 + '''> ?o.
                                          ?o <''' + p2 + '''> ?o2.
                                          ?o <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                            quc = quc1 + quc2

                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                          FROM<http://dbpedia-latest.org>{
                                          ?s <''' + p1 + '''> ?o.
                                          ?o <''' + p2 + '''> ?o2.
                                          ?o2 <''' + p3 + '''> ?o3.'''
                            if pattern[0] == structure[0][0]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[0][2]:
                                if pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o2 a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o2 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o2 a <''' + pattern[1][2] + '''>.}'''

                            elif pattern[0] == structure[1][2]:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[0][0]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?o3 a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?s a <''' + pattern[1][0] + '''>.
                                                  ?o3 a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?s a <''' + pattern[1][1] + '''>.
                                                  ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                  ?o3 a <''' + pattern[1][0] + '''>.
                                                  ?o a <''' + pattern[1][1] + '''>.
                                                  ?s a <''' + pattern[1][2] + '''>.}'''

                            else:
                                if pattern[1][0] == structure[0][2]:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                                elif pattern[1][0] == structure[1][2]:
                                    if pattern[1][1] == structure[1][0]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?s a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1][0] + '''>.
                                                 ?s a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''

                                else:
                                    if pattern[1][1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o2 a <''' + pattern[1][1] + '''>.
                                                 ?o a <''' + pattern[1][2] + '''>.}'''
                                    else:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1][0] + '''>.
                                                 ?o a <''' + pattern[1][1] + '''>.
                                                 ?o2 a <''' + pattern[1][2] + '''>.}'''

                            quc = quc1 + quc2

                else:
                    if len(structure) == 2:
                        if structure[0][0] == structure[1][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                                        ?s <''' + p1 + '''> ?o.
                                                                        ?s <''' + p2 + '''> ?o2.
                                                                       '''
                            if pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '}'
                            quc = quc1 + quc2

                        elif structure[0][2] == structure[1][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?o <''' + p2 + '''> ?o2.
                                           '''
                            if pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                else:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1] + '''>.}'''
                            else:
                                quc2 = '}'
                            quc = quc1 + quc2

                    elif len(structure) == 3 and len(structure[0]) == 3:
                        if structure[0][0] == structure[1][0]:
                            if structure[2][0] == structure[0][0]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                        FROM<http://dbpedia-latest.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?s <''' + p2 + '''> ?o2.
                                        ?s <''' + p3 + '''> ?o3.
                                                                            '''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[0][2]:
                                    if pattern[1] == structure[0][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                    ?s a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[1][2]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                else:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                quc = quc1 + quc2
                            elif structure[2][0] == structure[0][2]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                                                FROM<http://dbpedia-latest.org>{
                                                                ?s <''' + p1 + '''> ?o.
                                                                ?s <''' + p2 + '''> ?o2.
                                                                ?o <''' + p3 + '''> ?o3.
                                                                                       '''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[0][2]:
                                    if pattern[1] == structure[0][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                    ?s a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[1][2]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                else:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                quc = quc1 + quc2
                            else:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                                                FROM<http://dbpedia-latest.org>{
                                                                ?s <''' + p1 + '''> ?o.
                                                                ?s <''' + p2 + '''> ?o2.
                                                                ?o2 <''' + p3 + '''> ?o3.
                                                                                         '''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[0][2]:
                                    if pattern[1] == structure[0][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                    ?s a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[1][2]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                else:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                quc = quc1 + quc2

                        elif structure[0][2] == structure[1][0]:
                            if structure[2][0] == structure[0][0]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                        FROM<http://dbpedia-latest.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                        ?s <''' + p3 + '''> ?o3.
                                                                            '''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[0][2]:
                                    if pattern[1] == structure[0][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                    ?s a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[1][2]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                else:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                quc = quc1 + quc2
                            elif structure[2][0] == structure[0][2]:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                            FROM<http://dbpedia-latest.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?o <''' + p2 + '''> ?o2.
                                            ?o <''' + p3 + '''> ?o3.
                                                                                       '''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[0][2]:
                                    if pattern[1] == structure[0][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                    ?s a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[1][2]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                else:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                quc = quc1 + quc2
                            else:
                                p1 = structure[0][1]
                                p2 = structure[1][1]
                                p3 = structure[2][1]
                                quc1 = '''    select count distinct  * 
                                            FROM<http://dbpedia-latest.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?o <''' + p2 + '''> ?o2.
                                            ?o2 <''' + p3 + '''> ?o3.
                                                                                         '''
                                if pattern[0] == structure[0][0]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[0][2]:
                                    if pattern[1] == structure[0][0]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                    ?s a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                elif pattern[0] == structure[1][2]:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[0][0]:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?s a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                else:
                                    if pattern[1] == structure[0][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                    ?o a <''' + pattern[1] + '''>.}'''
                                    elif pattern[1] == structure[1][2]:
                                        quc2 = '''?o3 a <''' + pattern[0] + '''>.
                                                 ?o2 a <''' + pattern[1] + '''>.}'''
                                    else:
                                        quc2 = '''?s a <''' + pattern[0] + '''>.
                                                 ?o3 a <''' + pattern[1] + '''>.}'''
                                quc = quc1 + quc2

                    else:
                        if pattern[0] == structure[2]:
                            o = pattern[0]
                            s = pattern[1]
                            p = structure[1]
                            quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                    ?s a <''' + s + '''>.
                                                    ?o a <''' + o + '''>.
                                                    ?s <''' + p + '''> ?o.
                                                    }'''
                        else:
                            s = pattern[0]
                            o = pattern[1]
                            p = structure[1]
                            quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                    ?s a <''' + s + '''>.
                                                    ?o a <''' + o + '''>.
                                                    ?s <''' + p + '''> ?o.
                                                    }'''

            elif len(pattern) == 1:
                if len(structure) == 2:
                    if structure[0][0] == structure[1][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                ?s <''' + p1 + '''> ?o.
                                                ?s <''' + p2 + '''> ?o2.
                                                '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '}'
                        quc = quc1 + quc2
                    elif structure[0][2] == structure[1][0]:
                        p1 = structure[0][1]
                        p2 = structure[1][1]
                        quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                                ?s <''' + p1 + '''> ?o.
                                                                ?o <''' + p2 + '''> ?o2.
                                                                '''
                        if pattern[0] == structure[0][0]:
                            quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[0][2]:
                            quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                        elif pattern[0] == structure[1][2]:
                            quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                        else:
                            quc2 = '}'
                        quc = quc1 + quc2

                elif len(structure) == 1:
                    o = pattern[0]
                    p = structure[1]
                    quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{

                                                            ?s <''' + p + '''> ?o.
                                                            ?o a <''' + o + '''>.
                                                            }'''

                elif len(structure) == 3 and len(structure[0]) == 3:
                    if structure[0][0] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                    FROM<http://dbpedia-latest.org>{
                                    ?s <''' + p1 + '''> ?o.
                                    ?s <''' + p2 + '''> ?o2.
                                    ?s <''' + p3 + '''> ?o3.
                                                                        '''
                            if pattern[0] == structure[0][0]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                            else:
                                quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                            quc = quc1 + quc2
                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                            FROM<http://dbpedia-latest.org>{
                                                            ?s <''' + p1 + '''> ?o.
                                                            ?s <''' + p2 + '''> ?o2.
                                                            ?o <''' + p3 + '''> ?o3.
                                                                                   '''
                            if pattern[0] == structure[0][0]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                            else:
                                quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                            quc = quc1 + quc2
                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                                            FROM<http://dbpedia-latest.org>{
                                                            ?s <''' + p1 + '''> ?o.
                                                            ?s <''' + p2 + '''> ?o2.
                                                            ?o2 <''' + p3 + '''> ?o3.
                                                                                     '''
                            if pattern[0] == structure[0][0]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                            else:
                                quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                            quc = quc1 + quc2

                    elif structure[0][2] == structure[1][0]:
                        if structure[2][0] == structure[0][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                    FROM<http://dbpedia-latest.org>{
                                    ?s <''' + p1 + '''> ?o.
                                    ?o <''' + p2 + '''> ?o2.
                                    ?s <''' + p3 + '''> ?o3.
                                                                        '''
                            if pattern[0] == structure[0][0]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                            else:
                                quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                            quc = quc1 + quc2
                        elif structure[2][0] == structure[0][2]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                        FROM<http://dbpedia-latest.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                        ?o <''' + p3 + '''> ?o3.
                                                                                   '''
                            if pattern[0] == structure[0][0]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                            else:
                                quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                            quc = quc1 + quc2
                        else:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            p3 = structure[2][1]
                            quc1 = '''    select count distinct  * 
                                        FROM<http://dbpedia-latest.org>{
                                        ?s <''' + p1 + '''> ?o.
                                        ?o <''' + p2 + '''> ?o2.
                                        ?o2 <''' + p3 + '''> ?o3.
                                                                                     '''
                            if pattern[0] == structure[0][0]:
                                quc2 = '''?s a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                quc2 = '''?o a <''' + pattern[0] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                quc2 = '''?o2 a <''' + pattern[0] + '''>.}'''
                            else:
                                quc2 = '''?o3 a <''' + pattern[0] + '''>.}'''
                            quc = quc1 + quc2

                else:
                    if pattern[0] == structure[0]:
                        o = pattern[0]
                        p = structure[1]
                        quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                ?s a <''' + o + '''>.
                                                ?s <''' + p + '''> ?o.
                                                }'''
                    else:
                        o = pattern[0]
                        p = structure[1]
                        quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                                    ?o a <''' + o + '''>.
                                                                    ?s <''' + p + '''> ?o.
                                                                    }'''

            else:
                p = structure[1]
                quc = '''    select count distinct  ?o FROM<http://dbpedia-latest.org>{
                                                ?o a <''' + pattern + '''>.
                                                ?s <''' + p + '''> ?o.
                                                }'''

        elif mode == 0:
            if len(pattern) == 2:
                if pattern[0][0] == pattern[1][0]:
                    p1 = pattern[0][1]
                    p2 = pattern[1][1]
                    quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?s <''' + p2 + '''> ?o2.
                                            }'''
                elif pattern[0][2] == pattern[1][0]:
                    p1 = pattern[0][1]
                    p2 = pattern[1][1]
                    quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                            ?s <''' + p1 + '''> ?o.
                                                            ?o <''' + p2 + '''> ?o2.
                                                            }'''
            elif len(pattern) == 1:
                p = pattern[1]
                quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                        ?s <''' + p + '''> ?o.
                                        }'''
        # print(quc)
        jishu = DBpedia_query(quc, DBpedia_endpoint)[0][0]
        return int(jishu)

    def gfdverifier(self, RHS, LHS, suma, p):
        """
        compute if gfd is frequent and not redundant
        supp就是gfd满足这个图模式下的所有条目中gfd的这个条目占的比例
        conf置信度就是LHS满足的条件下，RHS满足这个gfd的占比
        :param entity:
        :param ty:
        :return:
        """
        ind = 0
        if LHS is None:
            supp = self.count(RHS, structure=p)  # 计算满足
            print('supp', supp)
            if supp > 150:
                ind = 1
        else:
            supp = self.count([RHS, LHS], structure=p)  # 计算满足
            print('supp', supp)
            if supp > 150:
                ind = 1

        return ind

    def bianli(self, list1, n):
        n = n - 1
        result = []
        for i in list1:
            ind = list1.index(i)
            ans = []
            if n != 0:
                list2 = list(list1[ind + 1:])
                temp = self.bianli(list2, n)
                for j in temp:
                    ans = list(j)
                    ans.append(i)
                    result.append(ans)
            else:
                ans.append(i)
                result.append(ans)
        return result

    def delete_pattern(self):
        ind = 0  # 指示第几层pattern
        for temp_Q in self.old_Q[1:]:
            # temp_Q is pattern list,eg.[<p1 e1 p2>,<p3 e2 p4>...]
            ind += 1
            for temp_Q1 in temp_Q:
                inde = 1
                _, entities = gen_query(temp_Q1)
                for entity in entities:
                    if entity[1:-2] in self.delete_Q:
                        inde = 0
                        print('DELETE ', temp_Q1)
                        break
                if inde:
                    self.Q[ind].append(temp_Q1)
                    print('ADD Q: ', temp_Q1)
                    for l in self.old_l[ind-1]:
                        # print(l)
                        for temp_l in l:
                            # print(temp_l)
                            for temp_l1 in temp_l[2]:
                                # print(temp_l1)
                                if temp_l1!=labeling(temp_Q1):
                                    self.l[ind-1].append(temp_l)
                                    print('ADD L : ',temp_l)
        print(self.Q,'\n',self.l)

        # 对应的gfd也要加入
        # self.l[ind].append(self.old_l[ind][temp_Q.index([temp_Q2])])

    def add_pattern(self, k=4):
        self.new_vspawn()
        self.new_hspawn()
        # for i in range(1, k + 1):
        #     for j in range(0, i):
        #         self.new_vspawn(i)
        #         self.new_hspawn(i, j)

    def update(self):
        self.new_Q_init()
        self.stream_manager()
        self.delete_pattern()
        self.add_pattern(k=3)
        # self.Q.append(self.new_Q)
        # self.l.append(self.new_l)
        print(self.V_t)


if __name__ == '__main__':
    ind=0
    Q = [[], [], [], []]
    qut = '''
    select  distinct ?p FROM<http://dbpedia-2016.org>{ 
    ?p rdfs:subClassOf* owl:Thing . 
    FILTER (REGEX(str(?p), "ontology", "i"))  
    }limit 200
    '''
    qt = DBpedia_query(qut, DBpedia_endpoint)[0]
    # print("qt =", qt)
    for t in qt:
        qtt = '''
        select count distinct ?p FROM<http://dbpedia-2016.org> { 
        ?p a <''' + t + '''> . 
        }
        '''
        tt = DBpedia_query(qtt, DBpedia_endpoint)[0][0]
        # print("tt =",tt)
        if int(tt) > 500:
            # print(t, 'is added, sum is', tt)
            # 1000 is minial support
            Q[0].append(t)
    que = '''
    SELECT  DISTINCT ?prop 
    FROM<http://dbpedia-2016.org>
    WHERE {
      ?prop a rdf:Property 
    }limit 100
    '''
    edge = DBpedia_query(que, DBpedia_endpoint)[0]
    # print(edge)
    for pattern in Q[0]:
        for e in edge:
            if ind>=500:
                # raise ("1000 over")
                break
            q1 = '''    select  distinct  ?o FROM<http://dbpedia-2016.org>{
            ?p a <''' + pattern + '''>.
            ?p <''' + e + '''> ?o.
            FILTER (!isLiteral(?o)). 
             }'''
            try:
                b = DBpedia_query1(q1, DBpedia_endpoint)
                time.sleep(1)
            except:
                b=[]
                print('ERROR b1',ind)
            if b:
                if len(b[0]) > 5:
                    # print('query count : ',q1)
                    #print('count :', b[0])
                    for temp in b[0]:
                        q2 = '''    select  distinct  ?p2 FROM<http://dbpedia-2016.org>{
                        <''' + temp + '''> a ?p2.
                        ?p2 rdfs:subClassOf* owl:Thing.
                        FILTER(!REGEX(str(?p2), owl:Thing, "i"))
                        }'''
                        try:
                            p2 = DBpedia_query1(q2, DBpedia_endpoint)
                            time.sleep(1)
                        except:
                            p2 = []
                            print('ERROR b2', ind)
                        if p2:
                            for _ in p2[0]:
                                temp1 = [pattern, e, _]
                                # print(temp,temp1)
                                if temp1 not in Q[1]:
                                    Q[1].append(temp1)
                                    print('Pattern ',ind,temp1,' added')
                                    ind = ind + 1

    # print('Q1:',ind, Q[1])
    ind = 0
    for pattern in Q[1]:
        # i=3
        for e in edge:
            if ind>=400:
                break
            query = [[], []]
            head = "select count distinct ?p FROM<http://dbpedia-2016.org>{"
            head1 = "select distinct ?p FROM<http://dbpedia-2016.org>{"
            end1 = "?p rdfs:subClassOf* owl:Thing.?o a ?p."
            end2 = '?p a ?'
            end = ' <' + e + '> ?o.FILTER(!REGEX(str(?p), owl:Thing, "i"))}'
            query[0], quentity = gen_query(pattern)
            for _ in quentity:
                query[1] = '?' + url_parse(_)[:-2]
                q = head1 + query[0] +end1+ query[1] + end
                # print(q)
                try:
                    b = DBpedia_query1(q, DBpedia_endpoint)
                    time.sleep(1)
                except:
                    print("b TIMEOUT: ", ind, q)
                    b = []
                if b:
                    for o in b[0]:
                        q2 = head+query[0]+ '?p a <' + o + '>.' +query[1]+' <'+e+'> ?p.}'
                        try:
                            b2 = DBpedia_query1(q2, DBpedia_endpoint)[0][0]
                            time.sleep(1)
                        except:
                            print("b2 TIMEOUT: ", ind, q2)
                            b2 = 0
                        if int(b2) >= 1:
                            # print("No %a time count is %a!"%(ind,b2))
                            if [_[1:-2],e,o]!=pattern and [pattern,[_[1:-2],e,o]] not in Q[2]:
                                Q[2].append([pattern,[_[1:-2],e,o]])
                                ind+=1
                                print('No.%a '%ind ,b2, [pattern, [_[1:-2], e, o]])

    ind = 0
    for pattern in Q[2]:
        # i=3
        for e in edge:
            if ind >= 300:
                break
            query = [[], []]
            head = "select count distinct ?p FROM<http://dbpedia-2016.org>{"
            head1 = "select distinct ?p FROM<http://dbpedia-2016.org>{"
            end1 = "?p rdfs:subClassOf* owl:Thing.?o a ?p."
            end2 = '?p a ?'
            end = ' <' + e + '> ?o.FILTER(!REGEX(str(?p), owl:Thing, "i"))}'
            query[0], quentity = gen_query(pattern)
            for _ in quentity:
                query[1] = '?' + url_parse(_)[:-2]
                q = head1 + query[0] + end1 + query[1] + end
                # print(q)
                try:
                    b = DBpedia_query1(q, DBpedia_endpoint)
                    time.sleep(1)
                except:
                    print("Q3 b TIMEOUT: ",ind, q)
                    b = []
                if b:
                    for o in b[0]:
                        q2 = head + query[0] + '?p a <' + o + '>.' + query[1] + ' <' + e + '> ?p.}'
                        # print(q2)
                        try:
                            b2 = DBpedia_query1(q2, DBpedia_endpoint)[0][0]
                            time.sleep(1)
                        except:
                            print(" Q3 b2 TIMEOUT: ",ind, q2)
                            b2 = 0
                        if int(b2) >= 1:
                            # print("No %a time count is %a!" % (ind, b2))
                            if [_[1:-2], e, o] != pattern[1] and [_[1:-2], e, o] != pattern[0] and \
                                    [pattern[0], pattern[1], [_[1:-2], e, o]] not in Q[3]:
                                Q[3].append([pattern[0], pattern[1], [_[1:-2], e, o]])
                                ind += 1
                                print('No.%a ' % ind, b2, [pattern[0], pattern[1], [_[1:-2], e, o]])
    print('\n', Q, '\n')
    ############################## L1 #############################
    l1 = [[], []]
    l1[0] = []
    # j=0
    RHS = LHS = []
    print('\n', '#' * 100, ' START Q1', '#' * 100)
    for pattern in Q[1]:
        # lo = Q[1].index(pattern)
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个pattern的个数
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = LHS = []
            RHS.append(entity[1:-2])
            # print(RHS)
            # print(entity)
            LHS = None
            print('\nADD dep: [', LHS, '--->', RHS, ']')
            inde = gfdverifier(RHS, LHS, suma, p=pattern)
            if inde and [LHS, RHS[0], labeling(pattern)] not in l1[0]:
                l1[0].append([LHS, RHS[0], labeling(pattern)])
                # l[0][1].append(RHS)
                # # Notice! need to find subclass
                # l[0][0].append(LHS)
                print('[', LHS, '--->', RHS, ']', 'Added complete!')
        print('-' * 200)
    print('#' * 100, ' Q1 OVER', len(l1[0]), '#' * 100, '\n')
    print("Level 1: l0:", len(l1[0]), "l1:", len(l1[1]), "\nQ:", len(Q[1]))
    for _ in l1[0][:15]: print(_, '\n')
    l1[1] = []
    # j=1

    print('\n', '#' * 100, ' START Q2', '#' * 100)
    for pattern in Q[1]:
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个graph的个数
        print('pattern sum = ', suma)
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = []
            LHS = []
            RHS.append(entity[1:-2])
            # print('RHS', RHS)
            for entity1 in entities:
                LHS = []
                if entity1[1:-2] != RHS[0]:
                    LHS.append(entity1[1:-2])
                    print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                    if LHS:
                        inde = gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                        # print(inde,'\n')
                        if inde:
                            temp2 = []
                            for temp2 in l1[1]:
                                q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                    {
                                    <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                    }'''
                                q_ask_L = '''ask FROM<http://dbpedia-2016.org>
                                    {
                                    <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                    }'''
                                if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                        or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                    inde = 0
                                    print(temp2, 'CANNOT ADD!!')
                                    break
                            if inde and [LHS[0], RHS[0], labeling(pattern)] not in l1[1]:
                                temp2 = []
                                for temp2 in l1[1]:
                                    q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                        }'''
                                    q_ask_L = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                        }'''
                                    if temp2[2][0] == labeling(pattern)  and \
                                            (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                             or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                        l1[1].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
                                l1[1].append([LHS[0], RHS[0], labeling(pattern)])
                                print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                ##########def reducedgfd():
                                temp2 = []
                                for temp2 in l1[0]:  # remove redundant gfd in l0
                                    if temp2[2][0] == labeling(pattern)  \
                                            and temp2[1] == RHS[0]:
                                        l1[0].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
    print('#' * 100, ' Q2 OVER', len(l1[0]), '#' * 100, '\n')
    print("Level1 : l0:", len(l1[0]), "l1:", len(l1[1]), "\nQ:", len(Q[1]))
    for _ in l1[1][:15]: print(_, '\n')

    ######################## L2 ############################
    l2 = [[], [], []]
    l2[0] = []
    # j=0
    RHS = LHS = []
    print('\n', '#' * 100, ' START Q1', '#' * 100)
    for pattern in Q[2]:
        # lo = Q[1].index(pattern)
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个pattern的个数
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = LHS = []
            RHS.append(entity[1:-2])
            # print(RHS)
            # print(entity)
            LHS = None
            print('\nADD dep: [', LHS, '--->', RHS, ']')
            inde = gfdverifier(RHS, LHS, suma, p=pattern)
            if inde and [LHS, RHS[0], labeling(pattern)] not in l2[0]:
                l2[0].append([LHS, RHS[0], labeling(pattern)])
                # l[0][1].append(RHS)
                # # Notice! need to find subclass
                # l[0][0].append(LHS)
                print('[', LHS, '--->', RHS, ']', 'Added complete!')
        print('-' * 200)
    print('#' * 100, ' Q1 OVER', len(l2[0]), '#' * 100, '\n')
    print("Level 2:  l0:", len(l2[0]), "l1:", len(l2[1]), "l2:", len(l2[2]),"\nQ:", len(Q[2]))
    for _ in l2[0][:15]: print(_, '\n')
    l2[1] = []
    # j=1

    print('\n', '#' * 100, ' START Q2', '#' * 100)
    for pattern in Q[2]:
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个graph的个数
        # print('pattern sum = ', suma)
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = []
            LHS = []
            RHS.append(entity[1:-2])
            # print('RHS', RHS)
            for entity1 in entities:
                LHS = []
                if entity1[1:-2] != RHS[0]:
                    LHS.append(entity1[1:-2])
                    print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                    if LHS:
                        inde = gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                        # print(inde,'\n')
                        if inde:
                            temp2 = []
                            for temp2 in l2[1]:
                                q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                        }'''
                                q_ask_L = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                        }'''
                                if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                        or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                    inde = 0
                                    print(temp2, 'CANNOT ADD!!')
                                    break
                            if inde and [LHS[0], RHS[0], labeling(pattern)] not in l2[1]:
                                temp2 = []
                                for temp2 in l2[1]:
                                    q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                            }'''
                                    q_ask_L = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                            }'''
                                    if (temp2[2] == labeling(pattern)) and \
                                            (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                             or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                        l2[1].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
                                l2[1].append([LHS[0], RHS[0], labeling(pattern)])
                                print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                ##########def reducedgfd():
                                temp2 = []
                                for temp2 in l2[0]:  # remove redundant gfd in l0
                                    if (temp2[2] == labeling(pattern))\
                                            and temp2[1] == RHS[0]:
                                        l2[0].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
    print('#' * 100, ' Q2 OVER', len(l2[1]), '#' * 100, '\n')
    print("Level 2:  l0:", len(l2[0]), "l1:", len(l2[1]),"l2:", len(l2[2]), "\nQ:", len(Q[2]))
    for _ in l2[1][:15]: print(_, '\n')

    l2[2] = []
    print('\n', '#' * 100, ' START Q3', '#' * 100)
    for pattern in Q[2]:
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个graph的个数
        # print('pattern sum = ', suma)
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = []
            LHS = []
            RHS.append(entity[1:-2])
            # print('RHS', RHS)
            for entity1 in entities:
                if entity1[1:-2] != RHS[0]:
                    LHS.append(entity1[1:-2])
            # LHS=[[],[]],RHS=[]
            if LHS and len(LHS) > 1:
                print('\nADD dep: [', LHS, '--->', RHS, ']')
                inde = gfdverifier(RHS[0], LHS, suma, p=pattern)
                # print(inde,'\n')
                if inde:
                    temp2 = []
                    for temp2 in l2[2]:
                        q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                {
                                <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                }'''
                        q_ask_L1 = '''ask FROM<http://dbpedia-2016.org>
                                {
                                <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                }'''
                        q_ask_L2 = '''ask FROM<http://dbpedia-2016.org>
                                {
                                <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                }'''
                        if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1):
                            inde = 0
                            print(temp2, 'CANNOT ADD!!')
                            break
                    if inde and [LHS, RHS[0], labeling(pattern)] not in l2[2]:
                        temp2 = []
                        for temp2 in l2[2]:
                            q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                    {
                                    <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                    }'''
                            q_ask_L1 = '''ask FROM<http://dbpedia-2016.org>
                                    {
                                    <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                    }'''
                            q_ask_L2 = '''ask FROM<http://dbpedia-2016.org>
                                    {
                                    <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                    }'''
                            if temp2[2]==labeling(pattern) and \
                                    (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                     or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                     DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
                                l2[2].remove(temp2)
                                print(temp2, 'REMOVED!!!')
                        l2[2].append([LHS, RHS[0], labeling(pattern)])
                        print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                        ##########def reducedgfd():
                        temp2 = []
                        for temp2 in l2[1]:  # remove redundant gfd in l0
                            if temp2[2]==labeling(pattern) \
                                    and temp2[1] == RHS[0] and temp2[0] in LHS:
                                l2[1].remove(temp2)
                                print(temp2, 'REMOVED!!!')
                        temp2 = []
                        for temp2 in l2[0]:  # remove redundant gfd in l0
                            if (temp2[2] == labeling(pattern)) \
                                    and temp2[1] == RHS[0]:
                                l2[0].remove(temp2)
                                print(temp2, 'REMOVED!!!')

    print('#' * 100, ' Q3 OVER', len(l2[2]), '#' * 100, '\n')
    print("Level 2:  l0:", len(l2[0]), "l1:", len(l2[1]),"l2:", len(l2[2]), "\nQ:", len(Q[2]))
    for _ in l2[2][:15]: print(_, '\n')


    ###################### L3 ###############################
    l3 = [[], [], [], []]
    ###################### 0
    l3[0] = []
    # j=0
    RHS = LHS = []
    print('\n', '#' * 100, ' START Q1', '#' * 100)
    for pattern in Q[3]:
        # lo = Q[1].index(pattern)
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个pattern的个数
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = LHS = []
            RHS.append(entity[1:-2])
            # print(RHS)
            # print(entity)
            LHS = None
            print('\nADD dep: [', LHS, '--->', RHS, ']')
            inde = gfdverifier(RHS, LHS, suma, p=pattern)
            if inde and [LHS, RHS[0], labeling(pattern)] not in l3[0]:
                l3[0].append([LHS, RHS[0], labeling(pattern)])
                # l[0][1].append(RHS)
                # # Notice! need to find subclass
                # l[0][0].append(LHS)
                print('[', LHS, '--->', RHS, ']', 'Added complete!')
        print('-' * 200)
    print('#' * 100, ' Q1 OVER', len(l3[0]), '#' * 100, '\n')
    print("Level 3:  l0:", len(l3[0]), "l1:", len(l3[1]), "l2:", len(l3[2]),"l3:", len(l3[3]), "\nQ:", len(Q[3]))
    for _ in l3[0][:15]: print(_, '\n')
    ###################### 1
    l3[1] = []
    # j=1
    print('\n', '#' * 100, ' START Q2', '#' * 100)
    for pattern in Q[3]:
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个graph的个数
        # print('pattern sum = ', suma)
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = []
            LHS = []
            RHS.append(entity[1:-2])
            # print('RHS', RHS)
            for entity1 in entities:
                LHS = []
                if entity1[1:-2] != RHS[0]:
                    LHS.append(entity1[1:-2])
                    print('\nADD dep: [', LHS[0], '--->', RHS[0], ']')
                    if LHS:
                        inde = gfdverifier(RHS[0], LHS[0], suma, p=pattern)
                        # print(inde,'\n')
                        if inde:
                            temp2 = []
                            for temp2 in l3[1]:
                                q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                            }'''
                                q_ask_L = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + temp2[0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                            }'''
                                if DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                        or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1):
                                    inde = 0
                                    print(temp2, 'CANNOT ADD!!')
                                    break
                            if inde and [LHS[0], RHS[0], labeling(pattern)] not in l3[1]:
                                temp2 = []
                                for temp2 in l3[1]:
                                    q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                                {
                                                <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                }'''
                                    q_ask_L = '''ask FROM<http://dbpedia-2016.org>
                                                {
                                                <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                                }'''
                                    if (temp2[2] == labeling(pattern)) and \
                                            (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                             or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                        l3[1].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
                                l3[1].append([LHS[0], RHS[0], labeling(pattern)])
                                print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                ##########def reducedgfd():
                                temp2 = []
                                for temp2 in l3[0]:  # remove redundant gfd in l0
                                    if (temp2[2] == labeling(pattern)) \
                                            and temp2[1] == RHS[0]:
                                        l3[0].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
    print('#' * 100, ' Q2 OVER', len(l3[1]), '#' * 100, '\n')
    print("Level 3:  l0:", len(l3[0]), "l1:", len(l3[1]), "l2:", len(l3[2]), "l3:", len(l3[3]),"\nQ:", len(Q[3]))
    for _ in l3[1][:15]: print(_, '\n')
    ################ 2
    l3[2] = []
    print('\n', '#' * 100, ' START Q3', '#' * 100)
    for pattern in Q[3]:
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个graph的个数
        # print('pattern sum = ', suma)
        _, entities = gen_query(pattern)
        for entity in entities:
            entities_cp=entities[:]
            entities_cp.remove(entity)
            RHS = []
            LHS = []
            LHS_list=[]
            temp2=[]
            RHS.append(entity[1:-2])
            # print('RHS', RHS)
            for i in range(len(entities_cp))[:-1]:
                for j in range(len(entities_cp))[1:]:
                    if j>i:
                        temp2.append(entities_cp[i][1:-2])
                        temp2.append(entities_cp[j][1:-2])
                        LHS_list.append(temp2)
                        temp2 = []
            for LHS in LHS_list:
                # LHS=[[],[]],RHS=[]
                if LHS and len(LHS) == 2:
                    print('\nADD dep: [', LHS, '--->', RHS, ']')
                    inde = gfdverifier(RHS[0], LHS, suma, p=pattern)
                    # print(inde,'\n')
                    if inde:
                        temp2 = []
                        for temp2 in l3[2]:
                            q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                        }'''
                            q_ask_L1 = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                        }'''
                            q_ask_L2 = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                        }'''
                            if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                    or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                    DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1):
                                inde = 0
                                print(temp2, 'CANNOT ADD!!')
                                break
                        if inde and [LHS, RHS[0], labeling(pattern)] not in l3[2]:
                            temp2 = []
                            for temp2 in l3[2]:
                                q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                            }'''
                                q_ask_L1 = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                            }'''
                                q_ask_L2 = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                            }'''
                                if temp2[2] == labeling(pattern) and \
                                        (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                         or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                         DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
                                    l3[2].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            l3[2].append([LHS, RHS[0], labeling(pattern)])
                            print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                            ##########def reducedgfd():
                            temp2 = []
                            for temp2 in l3[1]:  # remove redundant gfd in l0
                                if temp2[2] == labeling(pattern) \
                                        and temp2[1] == RHS[0] and temp2[0] in LHS:
                                    l3[1].remove(temp2)
                                    print(temp2, 'REMOVED!!!')
                            temp2 = []
                            for temp2 in l3[0]:  # remove redundant gfd in l0
                                if (temp2[2] == labeling(pattern)) \
                                        and temp2[1] == RHS[0]:
                                    l3[0].remove(temp2)
                                    print(temp2, 'REMOVED!!!')

    print('#' * 100, ' Q3 OVER', len(l3[2]), '#' * 100, '\n')
    print("Level 3:  l0:", len(l3[0]), "l1:", len(l3[1]), "l2:", len(l3[2]), "l3:",len(l3[3]),"\nQ:", len(Q[3]))
    for _ in l3[2][:15]: print(_, '\n')
    #################### 3
    l3[3] = []
    print('\n', '#' * 100, ' START Q4', '#' * 100)
    for pattern in Q[3]:
        print('\n', '-' * 200)
        print(pattern)
        RHS = LHS = []
        suma = 1  # 计算满足这个graph的个数
        # print('pattern sum = ', suma)
        _, entities = gen_query(pattern)
        for entity in entities:
            RHS = []
            LHS = []
            RHS.append(entity[1:-2])
            # print('RHS', RHS)
            for entity1 in entities:
                if entity1[1:-2] != RHS[0]:
                    LHS.append(entity1[1:-2])
            # LHS=[[],[]],RHS=[]
            if LHS and len(LHS) == 3:
                print('\nADD dep: [', LHS, '--->', RHS, ']')
                inde = gfdverifier(RHS[0], LHS, suma, p=pattern)
                # print(inde,'\n')
                if inde:
                    temp2 = []
                    for temp2 in l3[3]:
                        q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
                                        }'''
                        q_ask_L1 = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
                                        }'''
                        q_ask_L2 = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
                                        }'''
                        q_ask_L3 = '''ask FROM<http://dbpedia-2016.org>
                                        {
                                        <''' + temp2[0][2] + '''> rdfs:subClassOf <''' + LHS[2] + '''>.
                                        }'''
                        if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1) or \
                                DBpedia_query(q_ask_L3, DBpedia_endpoint, q_type=1):
                            inde = 0
                            print(temp2, 'CANNOT ADD!!')
                            break
                    if inde and [LHS, RHS[0], labeling(pattern)] not in l3[3]:
                        temp2 = []
                        for temp2 in l3[3]:
                            q_ask_R = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                            }'''
                            q_ask_L1 = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                            }'''
                            q_ask_L2 = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                            }'''
                            q_ask_L3 = '''ask FROM<http://dbpedia-2016.org>
                                            {
                                            <''' + LHS[2] + '''> rdfs:subClassOf <''' + temp2[0][2] + '''>.
                                            }'''
                            if temp2[2] == labeling(pattern) and \
                                    (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                     or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                     DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1) or \
                                        DBpedia_query(q_ask_L3, DBpedia_endpoint, q_type=1)):
                                l3[3].remove(temp2)
                                print(temp2, 'REMOVED!!!')
                        l3[3].append([LHS, RHS[0], labeling(pattern)])
                        print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                        ##########def reducedgfd():
                        temp2 = []
                        for temp2 in l3[2]:  # remove redundant gfd in l0
                            if temp2[2] == labeling(pattern) \
                                    and temp2[1] == RHS[0] and (temp2[0][0] in LHS)\
                                    and (temp2[0][1] in LHS):
                                l3[2].remove(temp2)
                                print(temp2, 'REMOVED!!!')
                        temp2 = []
                        for temp2 in l3[1]:  # remove redundant gfd in l0
                            if temp2[2] == labeling(pattern) \
                                    and temp2[1] == RHS[0] and (temp2[0] in LHS):
                                l3[1].remove(temp2)
                                print(temp2, 'REMOVED!!!')
                        temp = []
                        for temp2 in l3[0]:  # remove redundant gfd in l0
                            if (temp2[2] == labeling(pattern)) \
                                    and temp2[1] == RHS[0]:
                                l3[0].remove(temp2)
                                print(temp2, 'REMOVED!!!')

    print('#' * 100, ' Q4 OVER', len(l3[3]), '#' * 100, '\n')
    print("Level 3:  l0:", len(l3[0]), "l1:", len(l3[1]), "l2:", len(l3[2]),"l3:", len(l3[3]), "\nQ:", len(Q[3]))
    for _ in l3[3][:15]: print(_, '\n')

    ############################## UPDATE ######################################
    print( '\n','#' * 100, ' UPDATE',  '#' * 100, '\n')
    t=gfd_updater(Q=Q,k=3,gfd=[l1,l2,l3])
    t.update()


    # l=[[],[],[]]
    # l[0] = []
    # # j=0
    # RHS = LHS = []
    # print('\n','#'*100,' START Q1','#'*100)
    # for pattern in Q[2]:
    #     # lo = Q[1].index(pattern)
    #     print('\n','-'*200)
    #     print(pattern)
    #     RHS = LHS = []
    #     suma = count(pattern,mode=0)  # 计算满足这个pattern的个数
    #     _, entities = gen_query(pattern)
    #     for entity in entities:
    #         RHS = LHS = []
    #         RHS.append(entity[1:-2])
    #         # print(RHS)
    #         # print(entity)
    #         LHS = None
    #         print('\nADD dep: [', LHS, '--->', RHS, ']')
    #         inde = gfdverifier(RHS, LHS, suma,p=pattern)
    #         if inde and [LHS,RHS[0],[pattern[0][1],pattern[1][1]]] not in l[0]:
    #             l[0].append([LHS,RHS[0],[pattern[0][1],pattern[1][1]]])
    #             # l[0][1].append(RHS)
    #             # # Notice! need to find subclass
    #             # l[0][0].append(LHS)
    #             print('[', LHS, '--->', RHS, ']','Added complete!')
    #     print('-' * 200)
    # print('#' * 100, ' Q1 OVER', len(l[0]), '#' * 100, '\n')
    # print("l0:", len(l[0]), "l1:", len(l[1]), "\nQ:", len(Q[1]))
    # for _ in l[0][:5]: print(_, '\n')
    # l[1]=[]
    # # j=1
    #
    # print('\n', '#' * 100, ' START Q2', '#' * 100)
    # for pattern in Q[2]:
    #     print('\n','-'*200)
    #     print(pattern)
    #     RHS = LHS = []
    #     suma = count(pattern, mode=0)  # 计算满足这个graph的个数
    #     print('pattern sum = ',suma)
    #     _, entities = gen_query(pattern)
    #     for entity in entities:
    #         RHS = []
    #         LHS = []
    #         RHS.append(entity[1:-2])
    #         # print('RHS', RHS)
    #         for entity1 in entities:
    #             LHS = []
    #             if entity1[1:-2]!=RHS[0]:
    #                 LHS.append(entity1[1:-2])
    #                 print('\nADD dep: [',LHS[0],'--->',RHS[0],']')
    #                 if LHS:
    #                     inde = gfdverifier(RHS[0], LHS[0], suma,p=pattern)
    #                     # print(inde,'\n')
    #                     if inde:
    #                         for temp2 in l[1]:
    #                             q_ask_R='''ask
    #                             {
    #                             <'''+temp2[1]+'''> rdfs:subClassOf <'''+RHS[0]+'''>.
    #                             }'''
    #                             q_ask_L='''ask
    #                             {
    #                             <'''+temp2[0]+'''> rdfs:subClassOf <'''+LHS[0]+'''>.
    #                             }'''
    #                             if DBpedia_query(q_ask_L,DBpedia_endpoint,q_type=1) \
    #                                     or DBpedia_query(q_ask_R,DBpedia_endpoint,q_type=1):
    #                                 inde=0
    #                                 print(temp2, 'CANNOT ADD!!')
    #                                 break
    #                         if inde and [LHS[0],RHS[0],[pattern[0][1] ,pattern[1][1]]] not in l[1]:
    #                             for temp2 in l[1]:
    #                                 q_ask_R = '''ask FROM<http://dbpedia-2016.org>
    #                                 {
    #                                 <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
    #                                 }'''
    #                                 q_ask_L = '''ask FROM<http://dbpedia-2016.org>
    #                                 {
    #                                 <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
    #                                 }'''
    #                                 if temp2[2][0]==pattern[0][1] and temp2[2][1] ==pattern[1][1] and \
    #                                         (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
    #                                         or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
    #                                     l[1].remove(temp2)
    #                                     print(temp2, 'REMOVED!!!')
    #                             l[1].append([LHS[0],RHS[0],[pattern[0][1] ,pattern[1][1]]])
    #                             print('[', LHS, '--->', RHS, ']','ADDED COMPLETE!!!')
    #                             ##########def reducedgfd():
    #                             for temp2 in l[0]:# remove redundant gfd in l0
    #                                 if temp2[2][0]==pattern[0][1] and temp2[2][1] ==pattern[1][1]\
    #                                         and temp2[1]==RHS[0]:
    #                                     l[0].remove(temp2)
    #                                     print(temp2, 'REMOVED!!!')
    #
    #
    #                     ###########
    #     print('-' * 200)
    # print('#' * 100, ' Q2 OVER', '#' * 100, '\n')
    # for _ in l[1][:5]: print(_, '\n')
    # print("l0:",len(l[0]),"l1:",len(l[1]),"\nQ:",len(Q[1]))
    #
    # l[2] = []
    # # j=1
    #
    # print('\n', '#' * 100, ' START Q3', '#' * 100)
    # for pattern in Q[2]:
    #     print('\n', '-' * 200)
    #     print(pattern)
    #     RHS = LHS = []
    #     suma = count(pattern, mode=0)  # 计算满足这个graph的个数
    #     print('pattern sum = ', suma)
    #     _, entities = gen_query(pattern)
    #     for entity in entities:
    #         RHS = []
    #         LHS = []
    #         RHS.append(entity[1:-2])
    #         # print('RHS', RHS)
    #         for entity1 in entities:
    #             if entity1[1:-2] != RHS[0]:
    #                 LHS.append(entity1[1:-2])
    #         print('\nADD dep: [', LHS, '--->', RHS, ']')
    #         # LHS=[[],[]],RHS=[]
    #         if LHS and len(LHS)>1:
    #             inde = gfdverifier(RHS[0], LHS, suma, p=pattern)
    #             # print(inde,'\n')
    #             if inde:
    #                 for temp2 in l[2]:
    #                     q_ask_R = '''ask
    #                         {
    #                         <''' + temp2[1] + '''> rdfs:subClassOf <''' + RHS[0] + '''>.
    #                         }'''
    #                     q_ask_L1 = '''ask
    #                         {
    #                         <''' + temp2[0][0] + '''> rdfs:subClassOf <''' + LHS[0] + '''>.
    #                         }'''
    #                     q_ask_L2 = '''ask
    #                         {
    #                         <''' + temp2[0][1] + '''> rdfs:subClassOf <''' + LHS[1] + '''>.
    #                         }'''
    #                     if DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
    #                             or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
    #                             DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1):
    #                         inde = 0
    #                         print(temp2, 'CANNOT ADD!!')
    #                         break
    #                 if inde and [LHS, RHS[0], [pattern[0][1], pattern[1][1]]] not in l[2]:
    #                     for temp2 in l[2]:
    #                         q_ask_R = '''ask
    #                             {
    #                             <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
    #                             }'''
    #                         q_ask_L1 = '''ask
    #                             {
    #                             <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
    #                             }'''
    #                         q_ask_L2 = '''ask
    #                             {
    #                             <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
    #                             }'''
    #                         if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] and \
    #                                 (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
    #                                  or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)or \
    #                                     DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
    #                             l[2].remove(temp2)
    #                             print(temp2, 'REMOVED!!!')
    #                     l[2].append([LHS, RHS[0], [pattern[0][1], pattern[1][1]]])
    #                     print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
    #                     ##########def reducedgfd():
    #                     for temp2 in l[1]:  # remove redundant gfd in l0
    #                         if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] \
    #                                 and temp2[1] == RHS[0] and temp2[0] in LHS:
    #                             l[1].remove(temp2)
    #                             print(temp2, 'REMOVED!!!')
    #
    #                     ###########
    #     print('-' * 200)
    # print('#' * 100, ' Q3 OVER', '#' * 100, '\n')
    # for _ in l[2][:5]: print(_, '\n')
    # print("l0:", len(l[0]), "l1:", len(l[1]), "l2:", len(l[2]),"\nQ:", len(Q[1]))
    # l=[[],[]]
    # l[0] = []
    # # j=0
    # RHS = LHS = []
    # print('\n','#'*100,' START Q1','#'*100)
    # for pattern in Q[1]:
    #     # lo = Q[1].index(pattern)
    #     print('\n','-'*200)
    #     print(pattern)
    #     RHS = LHS = []
    #     suma = count(pattern,mode=0)  # 计算满足这个pattern的个数
    #     _, entities = gen_query(pattern)
    #     for entity in entities:
    #         RHS = LHS = []
    #         RHS.append(entity[1:-2])
    #         # print(RHS)
    #         # print(entity)
    #         LHS = None
    #         print('\nADD dep: [', LHS, '--->', RHS, ']')
    #         inde = gfdverifier(RHS, LHS, suma,p=pattern)
    #         if inde and [LHS,RHS[0],pattern[1]] not in l[0]:
    #             l[0].append([LHS,RHS[0],pattern[1]])
    #             # l[0][1].append(RHS)
    #             # # Notice! need to find subclass
    #             # l[0][0].append(LHS)
    #             print('[', LHS, '--->', RHS, ']','Added complete!')
    #     print('-' * 200)
    # print('#' * 100, ' Q1 OVER', len(l[0]), '#' * 100, '\n')
    # print("l0:", len(l[0]), "l1:", len(l[1]), "\nQ:", len(Q[1]))
    # for _ in l[0][:5]: print(_, '\n')
    # l[1]=[]
    # # j=1
    # print('\n', '#' * 100, ' START Q2', '#' * 100)
    # for pattern in Q[1]:
    #     print('\n','-'*200)
    #     print(pattern)
    #     RHS = LHS = []
    #     suma = count(pattern, mode=0)  # 计算满足这个graph的个数
    #     print('pattern sum = ',suma)
    #     _, entities = gen_query(pattern)
    #     for entity in entities:
    #         RHS = []
    #         LHS = []
    #         RHS.append(entity[1:-2])
    #         # print('RHS', RHS)
    #         for entity1 in entities:
    #             if entity1[1:-2]!=RHS[0]:
    #                 LHS.append(entity1[1:-2])
    #         print('\nADD dep: [',LHS,'--->',RHS,']')
    #         if LHS:
    #             inde = gfdverifier(RHS, LHS, suma,p=pattern)
    #             # print(inde,'\n')
    #             if inde:
    #                 for temp2 in l[1]:
    #                     q_ask_R='''ask
    #                     {
    #                     <'''+temp2[1]+'''> rdfs:subClassOf <'''+RHS[0]+'''>.
    #                     }'''
    #                     q_ask_L='''ask
    #                     {
    #                     <'''+temp2[0]+'''> rdfs:subClassOf <'''+LHS[0]+'''>.
    #                     }'''
    #                     if DBpedia_query(q_ask_L,DBpedia_endpoint,q_type=1) \
    #                             or DBpedia_query(q_ask_R,DBpedia_endpoint,q_type=1):
    #                         inde=0
    #                         print(temp2, 'CANNOT ADD!!')
    #                         break
    #                 if inde:
    #                     for temp2 in l[1]:
    #                         q_ask_R = '''ask
    #                         {
    #                         <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
    #                         }'''
    #                         q_ask_L = '''ask
    #                         {
    #                         <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
    #                         }'''
    #                         if temp2[2]==pattern and \
    #                                 (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
    #                                 or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
    #                             l[1].remove(temp2)
    #                             print(temp2, 'REMOVED!!!')
    #                     l[1].append([LHS[0],RHS[0],pattern[1]])
    #                     print('[', LHS, '--->', RHS, ']','ADDED COMPLETE!!!')
    #                     ##########def reducedgfd():
    #                     for temp2 in l[0]:# remove redundant gfd in l0
    #                         if temp2[2]==pattern[1] and temp2[1]==RHS[0]:
    #                             l[0].remove(temp2)
    #                             print(temp2, 'REMOVED!!!')
    #
    #
    #                     ###########
    #     print('-' * 200)
    # print('#' * 100, ' Q2 OVER', '#' * 100, '\n')
    # for _ in l[1][:5]: print(_, '\n')
    # print("l0:",len(l[0]),"l1:",len(l[1]),"\nQ:",len(Q[1]))
#      FILTER(!REGEX(str(?p2), owl:Thing, "i"))
#    if int(b[0]) >= 10:  # mining frequent patterns/edges
#      q1 = '''    select distinct  ?p2 FROM<http://dbpedia-latest.org>{
#    ?p a <''' + pattern + '''>.
#  ?p <''' + e + '''> ?o.
# ?o a ?p2.
#            ?p2 rdfs:subClassOf* owl:Thing.
#          FILTER(!REGEX(str(?p2), owl:Thing, "i")) }'''
#        print(q1)
#      b = DBpedia_query(q1, DBpedia_endpoint)[0]
#    print(b)
#  if b:



