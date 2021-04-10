from SPARQLWrapper import SPARQLWrapper, JSON
import urllib
import timeout_decorator

# import pyodbc
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
    # print(list2)
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


# def gen_query1(p):
#     """
#
#     :param p:三元组
#     :param e:边e
#     :return: 符合查询格式的查询
#     """
#     entity1 = []
#     entity2 = []
#     entity = []
#     result = ''
#     temp1 = []
#     if isinstance(p[0], list):
#         for p1 in p:
#             temp1, entity2 = gen_query(p1)
#             # temp1 is fixed pattern
#             result = result + temp1
#             for i in entity2:
#                 if i not in entity1:
#                     entity1.append(i)
#     else:
#         for _ in [0, 2]:
#             temp2 = '<' + p[_] + '> '
#             entity1.append(temp2)
#             # temp2 is entities
#         p1 = url_parse(p[0])
#         p2 = url_parse(p[2])
#         s1 = '?' + p1 + ' a <' + str(p[0]) + '>.'
#         e1 = '?' + p2 + ' a <' + str(p[2]) + '>.'
#         p1 = '?' + p1 + ' <' + str(p[1]) + '> ?' + p2 + '.'
#         result = s1 + e1 + p1
#     for i in entity1:
#         if i not in entity:
#             entity.append(i)
#     # print(result)
#     return result, entity

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


def qu_type(q):
    """

    :param q: query entity,eg.http://dbpedia.org/ontology/Film
    :return: all entity of this entity(type:list)
    """
    qu = '''select distinct ?q FROM<http://dbpedia-latest.org> {
    ?q a ''' + '<' + q + '>}'
    _, ans = DBpedia_query(qu, DBpedia_endpoint)
    return ans[0]


def qu_subclass(q):
    """
    query all subclass of a entity type,if there is no subclass of this
    type exist, that means that type is the minimal type
    :param q: query entity,eg.http://dbpedia.org/ontology/Agent
    :return: all subclass of this entity(type:list),eg.http://dbpedia.org/ontology/WrittenWork
    """
    qu = '''select distinct ?c {?c rdfs:subClassOf* <
    ''' + q + '''
    >FILTER (!REGEX(str(?c), '
    ''' + q + '''
    ', "i"))}'''
    _, ans = DBpedia_query(qu, DBpedia_endpoint)
    return ans[0]


class tree:
    """
    tree class
    """

    def __init__(self, k):
        """
        V节点是每一层的pattern，边E是由上一层的V指向下一层V‘的边
        :param k:
        """
        self.edge = []
        # edge是所有边的集合
        self.k = k  # k bound
        self.Q = [[] for _ in range(k + 1)]
        self.l = [[[] for _ in range(4)] for _ in range(4)]
        self.V_t = {'Q': self.Q, 'l': self.l}
        self.Q_init()
        # self.T=(self.V_t,self.E_t)

    def Q_init(self):
        """
        init Q[0]
        :return:
        """
        qut = '''
            select  distinct ?p FROM<http://dbpedia-latest.org>{ 
            ?p rdfs:subClassOf* owl:Thing . 
            FILTER (REGEX(str(?p), "ontology", "i"))  
            }limit 100
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

        qut = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select  distinct ?p FROM<http://dbpedia-latest.org>{ 
        ?p rdfs:subClassOf* owl:Thing . 
        FILTER (REGEX(str(?p), "ontology", "i"))  
        }limit 100

        '''
        qt = DBpedia_query(qut, DBpedia_endpoint)[0]
        for t in qt:
            qtt = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select count distinct ?p FROM<http://dbpedia-latest.org> { 
        ?p rdfs:type <''' + t + '''> . 
        }

        '''

            tt = DBpedia_query(qtt, DBpedia_endpoint)[0]
            if len(tt) >= 10:
                # 1000 is minial support
                self.Q[0].append(t)

    def vspawn(self, i):
        """
        纵向扩展生成树
        会查到重复的pattern例如[[a,b,c][d,e,f]]和[[d,e,f][a,b,c]]
        :param i: level i
        :return:
        """
        ind = 0
        if i == 1:
            for pattern in self.Q[0]:
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
                                            self.Q[1].append(temp1)
                                            # print('Pattern ',ind,temp1,' added')
                                            ind = ind + 1
        elif i == 2:
            ind = 0
            for pattern in self.Q[1]:
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
                                        self.Q[2].append([pattern, [_[1:-2], e, o]])
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

    # def count1(self, pattern):
    #     """
    #     count this pattern
    #     :param pattern:
    #     :return:
    #     """
    #     if len(pattern) == 3:
    #         s = pattern[0]
    #         o = pattern[2]
    #         p = pattern[1]
    #         quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
    #                     ?s a <''' + s + '''>.
    #                     ?o a <''' + o + '''>.
    #                     ?s <''' + p + '''> ?o.
    #                     }'''
    #
    #     elif len(pattern) == 2:
    #         s = pattern[0]
    #         o = pattern[1]
    #         quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
    #                                 ?s a <''' + s + '''>.
    #                                 ?o a <''' + o + '''>.
    #                                 ?s ?e ?o.
    #                                 }'''
    #     elif len(pattern) == 1:
    #         o = pattern[0]
    #         quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
    #                                 ?o a <''' + o + '''>.
    #                                 ?s ?e ?o.
    #                                 }'''
    #     jishu = DBpedia_query(quc, DBpedia_endpoint)
    #     return jishu

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
                    # if structure[0][0] == structure[1][0]:
                    #     p1 = structure[0][1]
                    #     p2 = structure[1][1]
                    #     quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                    #                                                 ?s <''' + p1 + '''> ?o.
                    #                                                 ?s <''' + p2 + '''> ?o2.
                    #                                                '''
                    #     if pattern[0][1] == structure[0][0]:
                    #         if pattern[1] == structure[0][2]:
                    #             quc2 = '''?s a <''' + pattern[0] + '''>.
                    #                         ?o a <''' + pattern[1] + '''>.}'''
                    #         elif pattern[1] == structure[1][2]:
                    #             quc2 = '''?s a <''' + pattern[0] + '''>.
                    #                         ?o2 a <''' + pattern[1] + '''>.}'''
                    #     elif pattern[0] == structure[0][2]:
                    #         if pattern[1] == structure[0][0]:
                    #             quc2 = '''?o a <''' + pattern[0] + '''>.
                    #                         ?s a <''' + pattern[1] + '''>.}'''
                    #         elif pattern[1] == structure[1][2]:
                    #             quc2 = '''?o a <''' + pattern[0] + '''>.
                    #                         ?o2 a <''' + pattern[1] + '''>.}'''
                    #     elif pattern[0] == structure[1][2]:
                    #         if pattern[1] == structure[0][0]:
                    #             quc2 = '''?o2 a <''' + pattern[0] + '''>.
                    #                         ?s a <''' + pattern[1] + '''>.}'''
                    #         elif pattern[1] == structure[0][2]:
                    #             quc2 = '''?o2 a <''' + pattern[0] + '''>.
                    #                         ?o a <''' + pattern[1] + '''>.}'''
                    #     quc = quc1 + quc2
                    # elif structure[0][2] == structure[1][0]:
                    #     p1 = structure[0][1]
                    #     p2 = structure[1][1]
                    #     quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                    #                     ?s <''' + p1 + '''> ?o.
                    #                     ?o <''' + p2 + '''> ?o2.
                    #                    '''
                    #     if pattern[0] == structure[0][0]:
                    #         if pattern[1] == structure[0][2]:
                    #             quc2 = '''?o a <''' + pattern[0] + '''>.
                    #                     ?o2 a <''' + pattern[1] + '''>.}'''
                    #         elif pattern[1] == structure[1][2]:
                    #             quc2 = '''?o2 a <''' + pattern[0] + '''>.
                    #                     ?o a <''' + pattern[1] + '''>.}'''
                    #     elif pattern[0] == structure[0][2]:
                    #         if pattern[1] == structure[0][0]:
                    #             quc2 = '''?s a <''' + pattern[0] + '''>.
                    #                     ?o2 a <''' + pattern[1] + '''>.}'''
                    #         elif pattern[1] == structure[1][2]:
                    #             quc2 = '''?o2 a <''' + pattern[0] + '''>.
                    #                     ?s a <''' + pattern[1] + '''>.}'''
                    #     elif pattern[0] == structure[1][2]:
                    #         if pattern[1] == structure[0][0]:
                    #             quc2 = '''?s a <''' + pattern[0] + '''>.
                    #                     ?o a <''' + pattern[1] + '''>.}'''
                    #         elif pattern[1] == structure[0][2]:
                    #             quc2 = '''?o a <''' + pattern[0] + '''>.
                    #                     ?s a <''' + pattern[1] + '''>.}'''
                    #     quc = quc1 + quc2
                    quc = []
                else:
                    if len(structure) == 2:
                        if structure[0][0] == structure[1][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                                        ?s <''' + p1 + '''> ?o.
                                                                        ?s <''' + p2 + '''> ?o2.
                                                                       '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                                ?o2 a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?s a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                                ?o a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2
                        elif structure[0][2] == structure[1][0]:
                            p1 = structure[0][1]
                            p2 = structure[1][1]
                            quc1 = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                            ?s <''' + p1 + '''> ?o.
                                            ?o <''' + p2 + '''> ?o2.
                                           '''
                            if pattern[0] == structure[0][0]:
                                if pattern[1] == structure[0][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[0][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o2 a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[1][2]:
                                    quc2 = '''?o2 a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1] + '''>.}'''
                            elif pattern[0] == structure[1][2]:
                                if pattern[1] == structure[0][0]:
                                    quc2 = '''?s a <''' + pattern[0] + '''>.
                                            ?o a <''' + pattern[1] + '''>.}'''
                                elif pattern[1] == structure[0][2]:
                                    quc2 = '''?o a <''' + pattern[0] + '''>.
                                            ?s a <''' + pattern[1] + '''>.}'''
                            quc = quc1 + quc2
                    else:
                        s = pattern[0][0]
                        o = pattern[1][0]
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
                        quc = quc1 + quc2

                elif len(structure) == 1 or len(structure) == 3:
                    o = pattern[0]
                    p = structure[1]
                    quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{

                                                            ?s <''' + p + '''> ?o.
                                                            ?o a <''' + o + '''>.
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
            else:
                p = pattern[1]
                quc = '''    select count distinct  * FROM<http://dbpedia-latest.org>{
                                                        ?s <''' + p + '''> ?o.
                                                        }'''
        # print(quc)
        jishu = DBpedia_query(quc, DBpedia_endpoint)[0][0]
        return int(jishu)

    def gfdverifier(self,RHS, LHS, suma, p):
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
            supp = self.count(RHS, structure=p) / suma  # 计算满足
            print('supp', supp)
            if supp > 0.05:
                ind = 1
        else:
            if len(LHS) == 2:
                ind = 1
            else:
                supp = self.count([RHS, LHS], structure=p) / suma  # 计算满足
                print('supp', supp)
                if supp > 0.05:
                    ind = 1

        return ind

    # def gfdverifier1(self, RHS, LHS, suma):
    #     """
    #     compute if gfd is frequent and not redundant
    #     supp就是gfd满足这个图模式下的所有条目中gfd的这个条目占的比例
    #     conf置信度就是LHS满足的条件下，RHS满足这个gfd的占比
    #     :param entity:
    #     :param ty:
    #     :return:
    #     """
    #     ind = 0
    #     if LHS:
    #         supp = self.count(RHS) / suma  # 计算满足
    #         if supp > 0.5:
    #             ind = 1
    #     else:
    #         supp = self.count([RHS, LHS]) / suma  # 计算满足
    #         if supp > 0.5:
    #             ind = 1
    #
    #     return ind

    def hspawn(self, i, j):
        """
        generate dependencies of level-i,in j where j range from [0,i]
        :param i: level-i
        :param j:
        :return: no return, verified dependencies are added to self.l
        """
        self.l[i][j] = []
        # the 2 list are LHS and RHS respectively
        RHS = LHS = []
        print('\n', '#' * 100, ' START Q1', '#' * 100)
        for pattern in self.Q[i]:
            RHS = LHS = []
            print('\n', '-' * 200)
            print(pattern)
            suma = self.count(pattern,mode=0)  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            if j == 0:
                for entity in entities:

                    RHS.append(entity[1:-2])
                    LHS = None
                    print('\nADD dep: [', LHS, '--->', RHS, ']')
                    ind = self.gfdverifier(RHS, LHS, suma,p=pattern)
                    if ind and [LHS,RHS[0],[pattern[0][1],pattern[1][1]]] not in self.l[0]:
                        self.l[i][j].append([LHS,RHS[0],[pattern[0][1],pattern[1][1]]])
                        # Notice! need to find subclass
                        print('[', LHS, '--->', RHS, ']', 'Added complete!')
            elif j == i+4:
                for entity in entities:
                    RHS = entity[1:-2]
                    for entity1 in entities:
                        if entity1 != entity:
                            LHS.append(entity1[1:-2])
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.l[i][j][1].append(RHS)
                        self.l[i][j][0].append(LHS)
            elif j==1:
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
                                    for temp2 in self.l[i][j]:
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
                                        for temp2 in self.l[i][j]:
                                            q_ask_R = '''ask
                                                        {
                                                        <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                        }'''
                                            q_ask_L = '''ask
                                                        {
                                                        <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0] + '''>.
                                                        }'''
                                            if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] and \
                                                    (DBpedia_query(q_ask_L, DBpedia_endpoint, q_type=1) \
                                                     or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1)):
                                                self.l[i][j].remove(temp2)
                                                print(temp2, 'REMOVED!!!')
                                        self.l[i][j].append([LHS[0], RHS[0], [pattern[0][1], pattern[1][1]]])
                                        print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                        ##########def reducedgfd():
                                        for temp2 in self.l[0]:  # remove redundant gfd in l0

                                            if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] \
                                                    and temp2[1] == RHS[0]:
                                                self.l[i][j-1].remove(temp2)
                                                print(temp2, 'REMOVED!!!')
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
            elif j==2:
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
                            for temp2 in self.l[i][j]:
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
                            if inde and [LHS, RHS[0], [pattern[0][1], pattern[1][1]]] not in self.l[i][j]:
                                for temp2 in self.l[i][j]:
                                    q_ask_R = '''ask
                                                    {
                                                    <''' + RHS[0] + '''> rdfs:subClassOf <''' + temp2[1] + '''>.
                                                    }'''
                                    q_ask_L1 = '''ask
                                                    {
                                                    <''' + LHS[0] + '''> rdfs:subClassOf <''' + temp2[0][0] + '''>.
                                                    }'''
                                    q_ask_L2 = '''ask
                                                    {
                                                    <''' + LHS[1] + '''> rdfs:subClassOf <''' + temp2[0][1] + '''>.
                                                    }'''
                                    if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] and \
                                            (DBpedia_query(q_ask_L1, DBpedia_endpoint, q_type=1) \
                                             or DBpedia_query(q_ask_R, DBpedia_endpoint, q_type=1) or \
                                             DBpedia_query(q_ask_L2, DBpedia_endpoint, q_type=1)):
                                        self.l[i][j].remove(temp2)
                                        print(temp2, 'REMOVED!!!')
                                self.l[i][j].append([LHS, RHS[0], [pattern[0][1], pattern[1][1]]])
                                print('[', LHS, '--->', RHS, ']', 'ADDED COMPLETE!!!')
                                ##########def reducedgfd():
                                for temp2 in self.l[i][j-1]:  # remove redundant gfd in l0
                                    if temp2[2][0] == pattern[0][1] and temp2[2][1] == pattern[1][1] \
                                            and temp2[1] == RHS[0] and temp2[0] in LHS:
                                        self.l[i][j-1].remove(temp2)
                                        print(temp2, 'REMOVED!!!')

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

    def generate_tree(self, k):
        """

        :param result: all entity attr
        :param k: k-bound GFD
        :return: GFD found
        """
        #
        # t=[[] for _ in range(k)]
        # t[0]=result

        print('Q:', self.Q)
        for i in range(1, k + 1):
            for j in range(0, i):
                print(i, j)
                self.vspawn(i)
                self.hspawn(i,j)
        #         print(self.l)
        #         j='<'+j+'>'
        #
        #         qs='''
        #         select  distinct ?p {
        #         ?p a
        #         '''
        #         qe='''
        #         }
        #         '''
        #         q=qs+j+qe
        #         print(q)
        #         temp=DBpedia_query(q,DBpedia_endpoint)
        #         # temp are entities in each attr
        #         if temp:
        #             print(temp)
        # gfd=t
        # return gfd


class gfd_updater:
    """
    GFD updater
    """

    def __init__(self, Q=[], k=4, gfd=[[], []]):
        self.old_Q = Q
        self.new_Q = [[] for _ in range(k - 1)]
        self.Q = [[] for _ in range(k - 1)]
        self.delete_Q = []
        self.old_l = gfd
        self.new_l = []
        self.l = []
        self.V_t = {'Q': self.Q, 'l': self.l}

    def new_Q_init(self):
        """
        init new Q[0]
        :return:
        """
        qut = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select  distinct ?p { 
        ?p rdfs:subClassOf* owl:Thing . 
        FILTER (REGEX(str(?p), "ontology", "i"))  
        }

        '''
        qt = DBpedia_query(qut, DBpedia_endpoint)[1][0]
        for t in qt:
            qtt = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select count distinct ?p {
        ?p rdfs:type <''' + t + '''> . 
        }

        '''
            tt = DBpedia_query(qtt, DBpedia_endpoint)[1][0]
            if tt >= 0:
                # 1000 is minial support
                self.Q[0].append(t)

    def stream_manager(self):
        for temp_Q in self.new_Q:
            if temp_Q not in self.old_Q[0]:
                self.new_Q[0].append(temp_Q)
                # Q is to be generate new GFD
        for temp_Q in self.old_Q[0]:
            if temp_Q not in self.new_Q:
                self.delete_Q.append(temp_Q)
                # delete_Q is going to be delete from GFDs

    def new_vspawn(self, i):
        """
        纵向扩展生成树
        会查到重复的pattern例如[[a,b,c][d,e,f]]和[[d,e,f][a,b,c]]
        :param i: level i
        :return:
        """
        if i == 1:
            for pattern in self.new_Q[0]:
                for e in self.edge:
                    q1 = '''    select count distinct  ?p FROM <http://dbpedia.org>{
                    ?p a <''' + pattern + '''>.
                    ?p <''' + e + '''> ?o.
                    ?p2 rdfs:subClassOf* owl:Thing.
                    ?o a ?p2.
                    FILTER(!REGEX(str(?p2), owl:Thing, "i")) }'''
                    b = DBpedia_query(q1, DBpedia_endpoint)[1][0]
                    if int(b[0]) >= 0:  # mining frequent patterns/edges
                        q1 = '''    select distinct  ?p2 FROM <http://dbpedia.org>{
                        ?p a <''' + pattern + '''>.
                        ?p <''' + e + '''> ?o.
                        ?p2 rdfs:subClassOf* owl:Thing.
                        ?o a ?p2.
                        FILTER(!REGEX(str(?p2), owl:Thing, "i")) }'''
                        b = DBpedia_query(q1, DBpedia_endpoint)[1][0]
                        if b:
                            for _ in b[0]:
                                temp = [pattern, e, _]
                                self.new_Q[1].append(temp)
        else:
            for pattern in self.new_Q[i - 1]:
                # i=3
                for e in self.edge:
                    query = [[], []]
                    head = "select count distinct ?p{"
                    head1 = "select distinct ?p{"
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
                                        if [_[1:-2], e, _1] not in pattern and temp not in self.new_Q[i]:
                                            self.new_Q[i].append(temp)
                                    else:
                                        temp = [pattern, [_[1:-2], e, _1]]
                                        if [_[1:-2], e, _1] != pattern and temp not in self.new_Q[i]:
                                            self.new_Q[i].append(temp)

    def count(self, pattern):
        """
        count this pattern
        :param pattern:
        :return:
        """
        if len(pattern) == 3:
            s = pattern[0]
            o = pattern[2]
            p = pattern[1]
            quc = '''    select count distinct  * FROM <http://dbpedia.org>{
                        ?s a <''' + s + '''>.
                        ?o a <''' + o + '''>.
                        ?s <''' + p + '''> ?o.
                        }'''
        elif len(pattern) == 2:
            s = pattern[0]
            o = pattern[1]
            quc = '''    select count distinct  * FROM <http://dbpedia.org>{
                                    ?s a <''' + s + '''>.
                                    ?o a <''' + o + '''>.
                                    ?s ?e ?o.
                                    }'''
        elif len(pattern) == 1:
            o = pattern[0]
            quc = '''    select count distinct  * FROM <http://dbpedia.org>{
                                    ?o a <''' + o + '''>.
                                    ?s ?e ?o.
                                    }'''
        jishu = DBpedia_query(quc, DBpedia_endpoint)
        return jishu

    def gfdverifier(self, RHS, LHS, suma):
        """
        compute if gfd is frequent and not redundant
        supp就是gfd满足这个图模式下的所有条目中gfd的这个条目占的比例
        conf置信度就是LHS满足的条件下，RHS满足这个gfd的占比
        :param entity:
        :param ty:
        :return:
        """
        ind = 0
        if LHS:
            supp = self.count(RHS) / suma  # 计算满足
            if supp > 0.5:
                ind = 1
        else:
            supp = self.count([RHS, LHS]) / suma  # 计算满足
            if supp > 0.5:
                ind = 1

        return ind

    def new_hspawn(self, i, j):
        """
        generate dependencies of level-i,in j where j range from [0,i]
        :param i: level-i
        :param j:
        :return: no return, verified dependencies are added to self.l
        """
        self.new_l[i][j] = [[], []]
        # the 2 list are LHS and RHS respectively
        RHS = LHS = []
        for pattern in self.new_Q[i]:
            RHS = LHS = []
            suma = self.count(pattern)  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            if j == 0:
                for entity in entities:
                    RHS = entity[1:-2]
                    LHS = None
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.new_l[i][j][1].append(RHS)
                        # Notice! need to find subclass
                        self.new_l[i][j][0].append(LHS)
            elif j == i:
                for entity in entities:
                    RHS = entity[1:-2]
                    for entity1 in entities:
                        if entity1 != entity:
                            LHS.append(entity1[1:-2])
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.new_l[i][j][1].append(RHS)
                        self.new_l[i][j][0].append(LHS)
            else:
                t_entity = self.bianli(entities, j)
                for entity in t_entity:
                    RHS = entity[1:-2]
                    for entity1 in entities:
                        if entity1 != entity:
                            LHS.append(entity1[1:-2])
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.new_l[i][j][1].append(RHS)
                        self.new_l[i][j][0].append(LHS)

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
                # temp_Q1 is pattern,eg.<p1 e p2>
                for temp_Q2 in self.delete_Q:
                    # temp_Q2 is delete pattern,eg.p1...
                    if temp_Q2 not in temp_Q1:
                        # 这里要迭代所有不包含delete的pattern，加入到对应的Q[i]
                        self.Q[ind].append(temp_Q1)
                        # 对应的gfd也要加入
                        self.l[ind].append(self.old_l[ind][temp_Q.index(temp_Q2)])

    def add_pattern(self, k=4):
        for i in range(1, k + 1):
            for j in range(0, i):
                self.new_vspawn(i)
                self.new_hspawn(i, j)

    def update(self):
        self.delete_pattern()
        self.add_pattern()
        self.Q.append(self.new_Q)
        self.l.append(self.new_l)


if __name__ == '__main__':
    # a=tree
    # a.vspawn(1)
    # V_t=[[] for _ in range(k)]
    # qu1q = '''
    # prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # SELECT distinct ?e
    # from <http://dbpedia.org>
    # WHERE {
    # [] a ?e.
    # } limit 100
    # '''
    # qut = '''
    # PREFIX prop: <http://dbpedia.org/property/>
    # PREFIX ont: <http://dbpedia.org/ontology/>
    # PREFIX res: <http://dbpedia.org/resource/>
    #
    # select  distinct ?p FROM<http://dbpedia-latest.org>{
    # ?p rdfs:subClassOf* owl:Thing .
    # FILTER (REGEX(str(?p), "ontology", "i"))
    # }
    # ORDER BY ?p
    # '''
    # # qut查询所有实体类型的
    #
    # que = '''
    # SELECT COUNT DISTINCT ?prop
    # FROM<http://dbpedia-latest.org>
    # WHERE {
    #   ?prop a rdf:Property
    # }
    # '''
    # # 查询所有边
    #
    # quq3 = '''
    # PREFIX prop: <http://dbpedia.org/property/>
    # PREFIX ont: <http://dbpedia.org/ontology/>
    # PREFIX res: <http://dbpedia.org/resource/>
    #
    # SELECT DISTINCT ?p ?o2 ?o3
    # FROM<http://dbpedia-latest.org>
    # WHERE {
    #   ?p a rdf:Property.
    #   <http://dbpedia.org/resource/Nature_(journal)>  ?p ?o.
    # #?o ?p2 ?o2.
    # optional{?o a ?o2.
    # <http://dbpedia.org/resource/Nature_(journal)> a ?o3.}
    #   #FILTER (REGEX(str(?p), "date", "i"))
    # }
    # '''

    # result = DBpedia_query(qut, DBpedia_endpoint)
    # print(result)
    # for i in result:
    #     _,data=url_parse(i)
    #     print(i,data,'\n')

    # T[0]=data
    T = tree(k=2)
    GFD = T.generate_tree(k=2)


