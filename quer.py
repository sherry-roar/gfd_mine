from SPARQLWrapper import SPARQLWrapper,JSON

DBpedia_endpoint = "http://dbpedia.org/sparql"
# DBpedia_endpoint = "http://localhost:8890/sparql"

def DBpedia_query(_query, kb_endpoint):
    """

    :param _query: sparql query statement
    :param kb_endpoint:
    :return:
    """
    sparql = SPARQLWrapper(kb_endpoint)
    sparql.setQuery(_query)
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()
    #print("response:",response)
    _,result = parse_query_result(response,1)
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
            ind=0
            for v in list1[i].values():
                list2[ind].append(v['value'])
                ind+=1
    #print("list2:",list2)
    return key,list2

if __name__=='__main__':
    Q=[[],[],[]]
    qut = '''
    select  distinct ?p FROM<http://dbpedia.org>{ 
    ?p rdfs:subClassOf* owl:Thing . 
    FILTER (REGEX(str(?p), "ontology", "i"))  
    }limit 3
    '''
    qt = DBpedia_query(qut, DBpedia_endpoint)[0]
    for t in qt:
        qtt = '''
        select count distinct ?p FROM<http://dbpedia.org> { 
        ?p a <''' + t + '''> . 
        }limit 100
        '''

        tt = DBpedia_query(qtt, DBpedia_endpoint)[0][0]
        if int(tt)>1000:
            print("tt =",tt)
            # 1000 is minial support
            Q[0].append(t)
    que = '''
    SELECT  DISTINCT ?prop 
    FROM<http://dbpedia.org>
    WHERE {
      ?prop a rdf:Property 
    }limit 3
    '''
    edge = DBpedia_query(que, DBpedia_endpoint)[0]
    for pattern in Q[0]:
        for e in edge:
            q1 = '''    select count distinct  ?p FROM<http://dbpedia-latest.org>{
            ?p a <''' + pattern + '''>.
            ?p <''' + e + '''> ?o.
            ?p2 rdfs:subClassOf* owl:Thing.
            ?o a ?p2.
            FILTER(!REGEX(str(?p2), owl:Thing, "i")) }'''
            b = DBpedia_query(q1, DBpedia_endpoint)[0]
            # dependencies sum
            if int(b[0]) >= 0:  # mining frequent patterns/edges
                q1 = '''    select distinct  ?p2 FROM<http://dbpedia-latest.org>{
                ?p a <''' + pattern + '''>.
                ?p <''' + e + '''> ?o.
                ?o a ?p2.
                ?p2 rdfs:subClassOf* owl:Thing.
                FILTER(!REGEX(str(?p2), owl:Thing, "i")) }'''
                b = DBpedia_query(q1, DBpedia_endpoint)[0]
                if b:
                    for _ in b[0]:
                        temp = [pattern, e, _]
                        Q[1].append(temp)
    print('Q1:', Q)


