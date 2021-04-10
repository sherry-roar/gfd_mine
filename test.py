from SPARQLWrapper import SPARQLWrapper,JSON
import urllib

DBpedia_endpoint = "https://dbpedia.org/sparql"
local_endpoint = "http://localhost:8890/sparql"

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

def parse_query_result(response,value):
    """

    :param response: dict type result
    :param value: value we want from dict
    :return:
    """
    list1 = response['results']['bindings']
    key=[]

    list2=[]
    if list1:
        for _ in list1[0].keys():
            key.append(_)
        l=len(key)
        list2=[[] for _ in range(l)]
        for i in range(len(list1)):
            # temp = [[] for _ in range(l)]
            ind=0
            for v in list1[i].values():
                # temp[ind].append(v['value'])
                list2[ind].append(v['value'])
                ind+=1
    # print(list2)
    return key,list2

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

if __name__ == '__main__':

    #     q1="""ask{
    # <http://dbpedia.org/ontology/Person> rdfs:subClassOf <http://dbpedia.org/ontology/Agent>.
    # }"""
    #     q2="""
    #     SELECT *
    #
    #     WHERE
    #
    #     {<"K.D. Joseph"> ?a ?b
    #
    #     }LIMIT 30"""
    #     result = DBpedia_query(q1, DBpedia_endpoint,q_type=1)
    #     if result:
    #         print(result,'==1')
    Q = [[],[],[]]
    Q[1]=[['http://dbpedia.org/ontology/Work', 'http://dbpedia.org/property/chiefeditor', 'http://dbpedia.org/ontology/Agent'],
          ['http://dbpedia.org/ontology/Work', 'http://dbpedia.org/property/chiefeditor', 'http://dbpedia.org/ontology/Person'],
          ['http://dbpedia.org/ontology/Work','http://dbpedia.org/property/chiefeditor','http://dbpedia.org/ontology/Journalist'],
          ['http://dbpedia.org/ontology/Work', 'http://dbpedia.org/property/chiefeditor', 'http://dbpedia.org/ontology/Politician'],
          ['http://dbpedia.org/ontology/Work', 'http://dbpedia.org/property/chiefeditor', 'http://dbpedia.org/ontology/Newspaper'],
          ['http://dbpedia.org/ontology/Work', 'http://dbpedia.org/property/chiefeditor', 'http://dbpedia.org/ontology/Writer']]
    edge = ['http://dbpedia.org/ontology/deathPlace','http://dbpedia.org/property/deathPlace',
            'http://dbpedia.org/ontology/deathDate','http://dbpedia.org/property/death',
            'http://dbpedia.org/ontology/birthPlace','http://dbpedia.org/ontology/birthDate','http://dbpedia.org/property/birth']
    for pattern in Q[1]:
        # i=3
        for e in edge:
            query = [[], []]
            head = "select count distinct ?p {"
            head1 = "select distinct ?p {"
            end1="?p rdfs:subClassOf* owl:Thing.?o a ?p."
            end = ' <' + e + "> ?o.}"
            query[0], quentity = gen_query(pattern)
            for _ in quentity:
                query[1] = '?' + url_parse(_)[:-2]
                q = head + query[0] + end1+query[1] + end
                print('q1',q)
                # b = DBpedia_query(q, DBpedia_endpoint)[1][0]
                b=1000
                if int(b) >= 100:
                    q = head1 + query[0] +end1+ query[1] + end
                    print('q2',q)
                    b1 = DBpedia_query(q, DBpedia_endpoint)
                    print(b1)
                    if b1:
                        for _1 in b[0]:
                            if isinstance(pattern[0], list):
                                temp = list(pattern)
                                temp.append([_[1:-2], e, _1])
                                if [_[1:-2], e, _1] not in pattern and temp not in Q[2]:
                                    Q[2].append(temp)
                            else:
                                temp = [pattern, [_[1:-2], e, _1]]
                                if [_[1:-2], e, _1] != pattern and temp not in Q[2]:
                                    Q[2].append(temp)