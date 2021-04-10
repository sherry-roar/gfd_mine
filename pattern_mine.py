from SPARQLWrapper import SPARQLWrapper,JSON
import urllib
# import pyodbc
DBpedia_endpoint = "https://dbpedia.org/sparql"
local_endpoint = "http://localhost:8890/sparql"




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
    # print(response)
    result = parse_query_result(response,1)
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
    # print(list2)
    return key,list2

def url_parse(url):
    url = urllib.parse.urlparse(url).path

    if url.rfind('/')==(len(url)-1):
        url=url[:-1]

    head=url.find('/')
    end=url.rfind('/')
    datetype =url[head+1:end]
    data=url[end+1:]
    return data

def gen_query(p):
    """

    :param p:三元组
    :param e:边e
    :return: 符合查询格式的查询
    """
    entity1=[]
    entity2=[]
    entity=[]
    result=''
    temp1=[]
    if isinstance(p[0],list):
        for p1 in p:
            temp1,entity2=gen_query(p1)
            # temp1 is fixed pattern
            result=result+temp1
            for i in entity2:
                if i not in entity1:
                    entity1.append(i)
    else:
        for _ in [0, 2]:
            temp2 = '<' + p[_] + '> '
            entity1.append(temp2)
            # temp2 is entities
        p1=url_parse(p[0])
        p2=url_parse(p[2])
        s1 = '?'+p1+' a <' + str(p[0]) + '>.'
        e1 = '?'+p2+' a <' + str(p[2]) + '>.'
        p1 = '?'+p1+' <' + str(p[1]) + '> ?'+p2+'.'
        result=s1+e1+p1
    for i in entity1:
        if i not in entity:
            entity.append(i)
    # print(result)
    return  result,entity

def qu_type(q):
    """

    :param q: query entity,eg.http://dbpedia.org/ontology/Film
    :return: all entity of this entity(type:list)
    """
    qu='''select distinct ?q{
    ?q a '''+'<'+q+'>}'
    _,ans=DBpedia_query(qu,DBpedia_endpoint)
    return ans[0]

def qu_subclass(q):
    """
    query all subclass of a entity type,if there is no subclass of this
    type exist, that means that type is the minimal type
    :param q: query entity,eg.http://dbpedia.org/ontology/Agent
    :return: all subclass of this entity(type:list),eg.http://dbpedia.org/ontology/WrittenWork
    """
    qu='''select distinct ?c {?c rdfs:subClassOf* <
    '''+q+'''
    >FILTER (!REGEX(str(?c), '
    '''+q+'''
    ', "i"))}'''
    _,ans=DBpedia_query(qu,DBpedia_endpoint)
    return ans[0]

class tree:
    """
    tree class
    """
    def __init__(self,k):
        """
        V节点是每一层的pattern，边E是由上一层的V指向下一层V‘的边
        :param k:
        """
        q = '''
        select distinct ?p
        {  
        ?p rdfs:subClassOf* owl:Thing.  
        FILTER(REGEX(str(?p), "ontology", "i"))  
        }limit 3
        '''
        que = '''
        SELECT  DISTINCT ?prop 
        WHERE {
          ?prop a rdf:Property #a是rdf:type的简写
        }limit 3
        '''
        # self.entity = DBpedia_query(q, DBpedia_endpoint)[1][0]
        # entity是所有实例集合
        self.edge=DBpedia_query(que,DBpedia_endpoint)[1][0]
        # edge是所有边的集合
        self.k=k #k bound
        self.Q=[[] for _ in range(k-1)]
        self.l=[]
        self.V_t={'Q':self.Q,'l':self.l}
        # self.T=(self.V_t,self.E_t)

    def Q_init(self):
        """
        init Q[0]
        :return:
        """
        qut = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select  distinct ?p { #WHERE在sparql中可省略
        ?p rdfs:subClassOf* owl:Thing . #加*表示此步操作需要迭代进行，不仅查找Person的子类还查找子类的子类；去掉*则只查找Person的子类
        FILTER (REGEX(str(?p), "ontology", "i"))  # "i"代表大小写不敏感，匹配?p中出现date
        }limit 3
        
        '''
        qt = DBpedia_query(qut, DBpedia_endpoint)[1][0]
        for t in qt:
            qtt = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select count distinct ?p { #WHERE在sparql中可省略
        ?p rdfs:type <'''+t+'''> . #加*表示此步操作需要迭代进行，不仅查找Person的子类还查找子类的子类；去掉*则只查找Person的子类
        }limit 3
        
        '''
            tt = DBpedia_query(qtt, DBpedia_endpoint)[1][0]
            if tt>=0 :
                # 1000 is minial support
                self.Q[0].append(t)

    def vspawn(self,i):
        """
        纵向扩展生成树
        会查到重复的pattern例如[[a,b,c][d,e,f]]和[[d,e,f][a,b,c]]
        :param i: level i
        :return:
        """
        if i==1:
            for pattern in self.Q[0]:
                for e in self.edge:
                    q1='''    select count distinct  ?p FROM <http://dbpedia.org>{
                    ?p a <'''+pattern+'''>.
                    ?p <'''+e+'''> ?o.
                    ?p2 rdfs:subClassOf* owl:Thing.
                    ?o a ?p2.
                    FILTER(!REGEX(str(?p2), owl:Thing, "i")) }limit 3'''
                    b=DBpedia_query(q1,DBpedia_endpoint)[1][0]
                    # dependencies sum
                    if int(b[0])>=0:# mining frequent patterns/edges
                        q1='''    select distinct  ?p2 FROM <http://dbpedia.org>{
                        ?p a <'''+pattern+'''>.
                        ?p <'''+e+'''> ?o.
                        ?o a ?p2.
                        ?p2 rdfs:subClassOf* owl:Thing.
                        FILTER(!REGEX(str(?p2), owl:Thing, "i")) }limit 3'''
                        b = DBpedia_query(q1, DBpedia_endpoint)[1][0]
                        if b:
                            for _ in b[0]:
                                temp=[pattern,e,_]
                                self.Q[1].append(temp)
        else:
            for pattern in self.Q[i-1]:
                # i=3
                for e in self.edge:
                    query = [[], []]
                    head = "select count distinct ?p{"
                    head1 = "select distinct ?p{"
                    end = ' <' + e + "> ?o." \
                                     "?p rdfs:subClassOf* owl:Thing." \
                                     "?o a ?p}limit 3"
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

    def count(self,pattern):
        """
        count this pattern
        :param pattern:
        :return:
        """
        if len(pattern)==3:
            s = pattern[0]
            o = pattern[2]
            p = pattern[1]
            quc = '''    select count distinct  * FROM <http://dbpedia.org>{
                        ?s a <''' + s + '''>.
                        ?o a <''' + o + '''>.
                        ?s <''' + p + '''> ?o.
                        }'''
        elif len(pattern)==2:
            s = pattern[0]
            o = pattern[1]
            quc = '''    select count distinct  * FROM <http://dbpedia.org>{
                                    ?s a <''' + s + '''>.
                                    ?o a <''' + o + '''>.
                                    ?s ?e ?o.
                                    }'''
        elif len(pattern)==1:
            o = pattern[0]
            quc = '''    select count distinct  * FROM <http://dbpedia.org>{
                                    ?o a <''' + o + '''>.
                                    ?s ?e ?o.
                                    }'''
        jishu = DBpedia_query(quc, DBpedia_endpoint)
        return jishu

    def gfdverifier(self,RHS, LHS, suma):
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

    def hspawn(self,i, j):
        """
        generate dependencies of level-i,in j where j range from [0,i]
        :param i: level-i
        :param j:
        :return: no return, verified dependencies are added to self.l
        """
        self.l[i][j] = [[], []]
        # the 2 list are LHS and RHS respectively
        RHS = LHS = []
        for pattern in self.Q[i]:
            RHS = LHS = []
            suma = self.count(pattern)  # 计算满足这个pattern的个数
            _, entities = gen_query(pattern)
            if j == 0:
                for entity in entities:
                    RHS = entity[1:-2]
                    LHS = None
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.l[i][j][1].append(RHS)
                        # Notice! need to find subclass
                        self.l[i][j][0].append(LHS)
            elif j==i:
                for entity in entities:
                    RHS = entity[1:-2]
                    for entity1 in entities:
                        if entity1 != entity:
                            LHS.append(entity1[1:-2])
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.l[i][j][1].append(RHS)
                        self.l[i][j][0].append(LHS)
            else:
                t_entity=self.bianli(entities,j)
                for entity in t_entity:
                    RHS = entity[1:-2]
                    for entity1 in entities:
                        if entity1 != entity:
                            LHS.append(entity1[1:-2])
                    ind = self.gfdverifier(RHS, LHS, suma)
                    if ind:
                        self.l[i][j][1].append(RHS)
                        self.l[i][j][0].append(LHS)


    def bianli(self,list1, n):
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

    def generate_tree(self,k):
        """

        :param result: all entity attr
        :param k: k-bound GFD
        :return: GFD found
        """
        #
        # t=[[] for _ in range(k)]
        # t[0]=result
        self.Q_init()
        for i in range(1,k+1):
            for j in range(0,i):
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
        }limit 3

        '''
        qt = DBpedia_query(qut, DBpedia_endpoint)[1][0]
        for t in qt:
            qtt = '''
        PREFIX prop: <http://dbpedia.org/property/>
        PREFIX ont: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>

        select count distinct ?p {
        ?p rdfs:type <''' + t + '''> . 
        }limit 3

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
                    FILTER(!REGEX(str(?p2), owl:Thing, "i")) }limit 3'''
                    b = DBpedia_query(q1, DBpedia_endpoint)[1][0]
                    if int(b[0]) >= 0:  # mining frequent patterns/edges
                        q1 = '''    select distinct  ?p2 FROM <http://dbpedia.org>{
                        ?p a <''' + pattern + '''>.
                        ?p <''' + e + '''> ?o.
                        ?p2 rdfs:subClassOf* owl:Thing.
                        ?o a ?p2.
                        FILTER(!REGEX(str(?p2), owl:Thing, "i")) }limit 3'''
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
                                     "?o a ?p}limit 3"
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

'''
#消极依赖没考虑，轴z没考虑，相关度简化，支持度简化，剪枝未考虑
1.首先查询所有边e
2.第一层储存所有的<x e y>三元组，这就是第一层的pattern。
  其中xy是满足<x e y>的匹配，即h(bar-x)是xy的集合，bar-x=[x,y]
3.第一层的依赖挖掘从0到1（层数）。首先从0层(j=0)开始，
  遍历节点（即遍历x，y，分别以x和y为root根l），第0层就是
  root依赖于空集（emptyset → l之类的）。第1层的依赖也是
  首先遍历根，分别是x为根，y为根，然后查找相应的满足的图模式（比如说对于create这条边
  的模式）(我认为依赖可以相互依赖，比如说电影依赖于制片人，制片人依赖于电影，
  然后根据支持度大小来决断是否保留，保留哪一个)
4.比如选择x为根，就找满足边e的所有主语x，然后x的对应的y，然后记录保留下来
  <x e y>，找新的之前先检测是不是有重复的，找到的重复的就把这个三元组的计数标记
  +1，然后计算相关度和支持度，然后确定一个阈值，达到的就认为这些依赖存在，由此完成第一轮挖掘
5.第二轮挖掘开始，把第一轮的树遍历出来（比如说x create y）固定x create y（?x <http://dbpedia.org/Property/create> ?y）
  然后搜索x或y是否有边延申（?x ?e []. ?e rdf:type ont:property.）然后查到的边添加进
  图模式（同样也要检查重复，不过一般不会重复）比如（<x birthdata z1,x create y>,<x create y, y obtain z2>）
  所有模式挖掘完成之后开始挖掘依赖
6.挖掘第二层的依赖也是从j=0~2,遍历所有根节点（xyz）
  
7.把第一层的图模式<s p o>中储存的谓语p拿出来，再查询新图的所有谓语
  
'''

if __name__=='__main__':
    # a=tree
    # a.vspawn(1)
    # V_t=[[] for _ in range(k)]
    qu1q='''
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT distinct ?e
    from <http://dbpedia.org>
    WHERE {
    [] a ?e.
    } limit 100
    '''
    qut='''
    PREFIX prop: <http://dbpedia.org/property/>
    PREFIX ont: <http://dbpedia.org/ontology/>
    PREFIX res: <http://dbpedia.org/resource/>

    select  distinct ?p { #WHERE在sparql中可省略
    ?p rdfs:subClassOf* owl:Thing . #加*表示此步操作需要迭代进行，不仅查找Person的子类还查找子类的子类；去掉*则只查找Person的子类
    FILTER (REGEX(str(?p), "ontology", "i"))  # "i"代表大小写不敏感，匹配?p中出现date
    }
    ORDER BY ?p
    '''
    # qut查询所有实体类型的

    que='''
    SELECT COUNT DISTINCT ?prop 
    WHERE {
      ?prop a rdf:Property #a是rdf:type的简写
    }
    '''
    # 查询所有边

    quq3='''
    PREFIX prop: <http://dbpedia.org/property/>
    PREFIX ont: <http://dbpedia.org/ontology/>
    PREFIX res: <http://dbpedia.org/resource/>
    
    SELECT DISTINCT ?p ?o2 ?o3
    WHERE {
      ?p a rdf:Property.
      <http://dbpedia.org/resource/Nature_(journal)>  ?p ?o.
    #?o ?p2 ?o2.
    optional{?o a ?o2.
    <http://dbpedia.org/resource/Nature_(journal)> a ?o3.}
      #FILTER (REGEX(str(?p), "date", "i"))  # "i"代表大小写不敏感，匹配?p中出现date
    }
    '''


    result=DBpedia_query(qut,DBpedia_endpoint)
    print(result)
    # for i in result:
    #     _,data=url_parse(i)
    #     print(i,data,'\n')

    # T[0]=data
    T=tree(k=2)
    GFD=T.generate_tree(k=2)


