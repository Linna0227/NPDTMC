import copy
import re
from pm4py.objects.process_tree.importer import importer as ptml_importer
from obj import Operator
from obj import ProcessTree
from pm4py.objects.process_tree.utils.generic import get_process_tree_height
from pm4py.objects.process_tree.utils.generic import is_leaf
from pm4py.objects.process_tree.utils.generic import is_tau_leaf
from pm4py.objects.process_tree.utils.generic import get_leaves
from pm4py.objects.process_tree.utils.generic import reduce_tau_leafs
from pm4py.visualization.process_tree import visualizer as pt_visualizer

#去掉所有不可见变迁
def reduce_tau_leaf(ProcessTree1):
    if len(ProcessTree1.children) > 0:
        for c in ProcessTree1.children:
            reduce_tau_leaf(c)
        for c in ProcessTree1.children:
            if is_tau_leaf(c):
                c.parent = None
                ProcessTree1.children.remove(c)
                break

#判断当前节点是否有孩子
def have_child(node) -> bool:
    if node._get_children() == None:
        return False
    else:
        return True

#判断当前节点是否有父节点
def have_parent(node) -> bool:
    if node._get_parent() == None:
        return False
    else:
        return True

#判断所有的孩子节点是否都是叶子节点
def all_leaf_child(node) -> bool:
    node_children = node._get_children()
    if have_child(node) == False:
        return False
    else:
        num = len(node_children)
        for inode in node_children:
            if have_child(inode):
                num -= 1;
                return False
        if num == len(node_children):
            return True
# for current_node in root_children:
#     print("get all_leaf_child***********------>", all_leaf_child(current_node))


#层次遍历得到最底层叶子节点
def t(Tree):
    root = Tree._get_root()
    if root._get_children() != list():
        child_nodes = root._get_children()
        getleaves = True
        while getleaves:
            leaves_to_replace = list()
            new_childnodes = list()
            for child in child_nodes:
                if child._get_children() != list():
                    leaves_to_replace.append(child)
            if leaves_to_replace != list():
                for child in leaves_to_replace:
                    for el in child.children:
                        new_childnodes.append(el)
                child_nodes = new_childnodes
            else:
                getleaves = False
    return child_nodes
# print("t(tree)===",t(tree))

# 根据孩子节点得到父节点列表（其中用到了集合转列表）
def use_parent_classify_leaves(list1):
    parents_set0 = set()
    for x in list1:
        parents_set0.add(x._get_parent())
        parents_list = list(parents_set0)
    return parents_list
# print("parent node/treelist-----> ",use_parent_classify_leaves(t(tree)))

#得到具体操作符列表
def get_nodeList_operator(parentList):
    node_name = list()
    for i in parentList:
        node_name.append(i.operator)
    return node_name

# treelist = use_parent_classify_leaves(t(tree))
# print("node_name---->",get_nodeList_operator(treelist))


#得到当前节点的孩子节点，key->操作符:value->操作符对应所有孩子节点
def get_operator_child_dic(list_of_tree):
    ope_child_dic = dict()
    x = list_of_tree.operator
    y = list_of_tree._get_children()
    ope_child_dic.update({x:y})
    return ope_child_dic
# treelist = use_parent_classify_leaves(t(tree))
# for j in treelist:
#     print("get_operator_child_dic---->", get_operator_child_dic(j))

#得到列表中所有操作符及其孩子节点，ex. [{->: [e2, f, g]}, {->: [p, r]}]
def get_operator_child_list(list_of_tree):
    list_all = list()
    for j in list_of_tree:
        list_all.append(get_operator_child_dic(j))
    return list_all
# treelist = use_parent_classify_leaves(t(tree))
# print("*******get_operator_child_list---->", get_operator_child_list(treelist))


#判断当前节点是否是重命名后的结点
def contain_rename_node(xnode) -> bool:
    reg1 = "StartSet:"
    reg2 = "EndSet:"
    xx = str(xnode._get_label())
    # print("&&&&xx->",xx)
    if (reg1 in xx) and (reg2 in xx):
        return True
    else:
        return False
# for i in t(tree):
#     print("contain_rename_node(",i,")----->",contain_rename_node(i))


#根据结点标签字符串得到startSet
def get_startSet_from_str(xnode_str):
    xx0 = re.findall(r'StartSet:{(.*)} \+ EndSet:', str(xnode_str))
    # print("startset_strxx000000000000000000----------------->", xx0)
    for i in xx0:
        xx = re.sub(r'["\']|["\']', '', str(i))
    # print("startset_strxxxxxxxxxxxxxxxxxx----------------->", xx)
    label_StartSet = set()
    reg1 = ','
    # zz = "a,b,ad,dcf"

    if reg1 in xx:
        y2 = xx.split(", ")
        # print("y2*************",y2)
        label_StartSet.update(y2)
        # print("label_StartSetyyyyyyyyyyyyyyyy2",label_StartSet)
    else:
        #单个字符组合成字符串
        liststr = list()
        liststr.append(xx)
        label_StartSet.update(liststr)
        # print("label_StartSet_Xxxxxxxxxxxxx",label_StartSet)
    return label_StartSet

# for i in t(tree):
#     print("label_startSet---=>",get_startSet_from_str(i))


#根据结点标签字符串得到EndSet
def get_endSet_from_str(xnode_str):
    #label_list = xnode._get_label()
    # print("xnode._get_label()----------------->",xnode._get_label())
    # print("label_list----------------->", label_list)
    yy0 = re.findall(r'EndSet:{(.*)} \+ TARSet:', str(xnode_str))
    # print("yyendset_str----------------->", yy0)
    for i in yy0:
        yy = re.sub(r'["\']|["\']', '', str(i))
    label_EndSet = set()
    reg1 = ','
    # xx = "a,b,ad,dcf"
    if reg1 in yy:
        y2 = yy.split(", ")
        label_EndSet.update(y2)
    else:
        # 单个字符组合成字符串
        liststr = list()
        liststr.append(yy)
        label_EndSet.update(liststr)
    return label_EndSet

# for i in t(tree):
#     print("label_EndSet---=>",get_endSet_from_str(i))

#根据结点标签字符串得到TARSet
def get_tarSet_from_str(xnode_str):
    zz = re.findall(r'TARSet:{(.*)}', str(xnode_str))
    # print("zztarset_Str----------------->", zz)
    label_TARSet = set()
    for i in range(len(zz)):
         xx1 = zz[i]
         reg2 = ','
         if reg2 in xx1:
             # print("yes!!!!!!!!!")
             res = re.sub(r'\'|\'', '', xx1)
             # print("res===>",res)
             y3 = res.split(", ")
             # print("y3",y3)
             label_TARSet.update(y3)
             # print("label_EndSet.update(y3)%%%%%%%",label_TARSet)
         else:
             # print("no!!!!")
             res = re.findall(r'\'(.*)\'', xx1)
             # res = re.sub(r'\'|\'', '', xx1)
             # print("res:@@@@@@@@@@@@",res)
             label_TARSet.update(res)
             # print("label_endset>>>>>>>>",label_TARSet)
    return label_TARSet

# for i in t(tree):
#     print("$$$$$$$$$label_tarSet---=>",get_tarSet_from_str(i))

#得到孩子节点的替换字符串
def get_leaf_StartSet(xnode):
    leaf_StartSet = set()
    leaf_StartSet.add(xnode)
    return leaf_StartSet

def get_leaf_EndSet(xnode):
    Seq_EndSet = set()
    Seq_EndSet.add(xnode)
    return Seq_EndSet

def get_leaf_TARSet(xnode):
    Seq_EndSet = set()
    return Seq_EndSet

def rename_leaf_node(xnode):
    node_str_SE=list()
    node_str_SE.append('LeafNode + StartSet:' + str(get_leaf_StartSet(xnode)) + ' + EndSet:' + str(get_leaf_EndSet(xnode)) + ' + TARSet:' + str(get_leaf_TARSet(xnode)))
    return node_str_SE
# for i in t(tree):
#     print("rename_leaf_node(i)========>",rename_leaf_node(i))


#输入节点，输出该节点改变后的样子
def LeafNode2Label(xnode):
    node_label = rename_leaf_node(xnode)
    node_parent = xnode._get_parent()
    # 创建一个新结点new_child，父节点设为node_parent
    new_child = ProcessTree(children=None, label=str(node_label), parent=node_parent)
    return new_child


#if node.operator == Operator.XOR 选择/ Operator.SEQUENCE 顺序 / Operator.PARALLEL 并发 / Operator.LOOP 循环
#1. Operator.SEQUENCE 顺序(输入的是叶子节点列表)
def get_seq_StartSet(nodeList):
    Seq_StartSet = set()
    # print("1.nodelist----->",nodeList)
    # print("nodelist[0]",nodeList[0])
    str_nodelist0 = str(nodeList[0])
    Seq_StartSet.update(get_startSet_from_str(str_nodelist0))
    # Seq_StartSet.add(nodeList[0])
    return Seq_StartSet
# print("seqStartSet---->",get_seq_StartSet(t(tree)))

def get_seq_EndSet(nodeList):
    Seq_EndSet = set()
    str_nodelist0 = str(nodeList[len(nodeList)-1])
    # print("&&&&&&&&&str_nodelist0endset", str_nodelist0)
    child_endset = get_endSet_from_str(str_nodelist0)
    # print("&&&&&&&&&&&&&&&&child_endset", child_endset)
    # Seq_EndSet.add(nodeList[len(nodeList)-1])
    Seq_EndSet.update(child_endset)
    return Seq_EndSet
# print("seqEndSet---->",get_seq_EndSet(t(tree)))

def get_seq_TARSet(nodeList):
    Seq_TarSet = set()
    if len(nodeList) == 1:
        for zz in range(len(nodeList)):
            str_nodelist0 = str(nodeList[zz])
            child_tarset0 = get_tarSet_from_str(str_nodelist0)
            Seq_TarSet.update(child_tarset0)
    for a in range(len(nodeList)-1):
        str_nodelist0 = str(nodeList[a])
        str_nodelist1 = str(nodeList[a+1])
        child0_endset = get_endSet_from_str(str_nodelist0)
        child1_startset = get_startSet_from_str(str_nodelist1)
        for i in child0_endset:
            for j in child1_startset:
                combination = i + '->' + j
                list_str = list()
                list_str.append(combination)
                # print("combination================>",list_str)
                Seq_TarSet.update(list_str)
        # Seq_TarSet.add(combination)
    for b in range(len(nodeList)):
        str_nodelist = str(nodeList[b])
        child_tarset = get_tarSet_from_str(str_nodelist)
        Seq_TarSet.update(child_tarset)
    return Seq_TarSet
# print("seqTARSet---->",get_seq_TARSet(t(tree)))


#2.Operator.XOR 选择(输入的是叶子节点列表)
def get_xor_StartSet(nodeList):
    xor_StartSet = set()
    for a in range(len(nodeList)):
         str_nodelist0 = str(nodeList[a])
         xor_StartSet.update(get_startSet_from_str(str_nodelist0))
         # Seq_StartSet.add(nodeList[0])
    #    xor_StartSet.add(nodeList[a])
    return xor_StartSet
# print("xorStartSet---->",get_xor_StartSet((t(tree))))

def get_xor_EndSet(nodeList):
    xor_EndSet = set()
    for b in range(len(nodeList)):
        str_nodelist0 = str(nodeList[b])
        xor_EndSet.update(get_endSet_from_str(str_nodelist0))
        # xor_EndSet.add(nodeList[b])
    return xor_EndSet
# print("xorEndSet---->",get_xor_EndSet(t(tree)))


def get_xor_TARSet(nodeList):
    xor_TarSet = set()
    if len(nodeList) == 1:
        for zz in range(len(nodeList)):
            str_nodelist0 = str(nodeList[zz])
            # child_tarset0 = get_tarSet_from_str(str_nodelist0)
            # xor_TarSet.update(child_tarset0)
            xor_TarSet.update(get_tarSet_from_str(str_nodelist0))
    for b in range(len(nodeList)):
        str_nodelist = str(nodeList[b])
        # child_tarset = get_tarSet_from_str(str_nodelist)
        # xor_TarSet.update(child_tarset)
        xor_TarSet.update(get_tarSet_from_str(str_nodelist))
    return xor_TarSet
# print("xorTARSet---->",get_xor_TARSet(t(tree)))


#3. Operator.PARALLEL 并发(输入的是叶子节点列表)
def get_parallel_StartSet(nodeList):
    parallel_StartSet = set()
    for a in range(len(nodeList)):
        str_nodelist0 = str(nodeList[a])
        # print("str_nodelist0Startset",str_nodelist0)
        child_startset = set()
        child_startset.update(get_startSet_from_str(str_nodelist0))
        # print("~~~~~~~~~~~~~~~~~~~~~~~child_startset~~~~~~~~~~~~~~~~",child_startset)
        # child_startset = get_startSet_from_str(str_nodelist0)
        parallel_StartSet.update(child_startset)
        # print("parallel_StartSet.update>>>>>>>>>>>>>>>>>>>>>>>>>>",parallel_StartSet)
        # Seq_StartSet.add(nodeList[0])
        # parallel_StartSet.add(nodeList[a])
    return parallel_StartSet
# print("parallelStartSet---->",get_parallel_StartSet(t(tree)))

def get_parallel_EndSet(nodeList):
    parallel_EndSet = set()
    for b in range(len(nodeList)):
        str_nodelist0 = str(nodeList[b])
        parallel_EndSet.update(get_endSet_from_str(str_nodelist0))
        # parallel_EndSet.add(nodeList[b])
    return parallel_EndSet
# print("parallelEndSet---->",get_parallel_EndSet(t(tree)))

def get_parallel_TARSet(nodeList):
    parallel_TarSet = set()
    if len(nodeList) == 1:
        for zz in range(len(nodeList)):
            str_nodelist0 = str(nodeList[zz])
            # child_tarset0 = get_tarSet_from_str(str_nodelist0)
            # parallel_TarSet.update(child_tarset0)
            parallel_TarSet.update(get_tarSet_from_str(str_nodelist0))
    for i in range(len(nodeList)):
        for j in range(len(nodeList)):
            if i != j:
                str_nodelist0 = str(nodeList[i])
                str_nodelist1 = str(nodeList[j])
                child0_endset = get_endSet_from_str(str_nodelist0)
                child1_startset = get_startSet_from_str(str_nodelist1)
                for ii in child0_endset:
                    for jj in child1_startset:
                        combination = ii + '->' + jj
                        list_str = list()
                        list_str.append(combination)
                        # print("combination================>",list_str)
                        parallel_TarSet.update(list_str)
    for z in range(len(nodeList)):
        str_nodelist = str(nodeList[z])
        child_tarset = get_tarSet_from_str(str_nodelist)
        parallel_TarSet.update(child_tarset)
    return parallel_TarSet
# print("parallelTARSet---->",get_parallel_TARSet(t(tree)))

#4. Operator.LOOP 循环(输入的是叶子节点列表)
def get_loop_StartSet(nodeList):
    loop_StartSet = set()
    str_nodelist0 = str(nodeList[0])
    # print("str_nodelist0Startset",str_nodelist0)
    child_startset = get_startSet_from_str(str_nodelist0)
    # print("child_startset",child_startset)
    loop_StartSet.update(child_startset)
    # loop_StartSet.add(nodeList[0])
    return loop_StartSet
# print("loopStartSet---->",get_loop_StartSet(t(tree)))

def get_loop_EndSet(nodeList):
    loop_EndSet = set()
    str_nodelist0 = str(nodeList[0])
    # print("str_nodelist0Startset",str_nodelist0)
    child_startset = get_startSet_from_str(str_nodelist0)
    # print("child_startset",child_startset)
    loop_EndSet.update(child_startset)
    # loop_EndSet.add(nodeList[0])
    return loop_EndSet
# print("loopEndSet---->",get_loop_EndSet(t(tree)))

def get_loop_TARSet(nodeList):
    loop_TarSet = set()
    if len(nodeList) == 1:
        for zz in range(len(nodeList)):
            str_nodelist0 = str(nodeList[zz])
            child_tarset0 = get_tarSet_from_str(str_nodelist0)
            loop_TarSet.update(child_tarset0)
    else:
        for a in range(len(nodeList) - 1):
            str_nodelist0 = str(nodeList[a])
            str_nodelist1 = str(nodeList[a + 1])
            str_nodelist2 = str(nodeList[0])
            child0_endset = get_endSet_from_str(str_nodelist0)
            child1_startset = get_startSet_from_str(str_nodelist1)
            child1_endset = get_endSet_from_str(str_nodelist1)
            child2_startset = get_startSet_from_str(str_nodelist2)
            if a == len(nodeList) - 2:
                for p in child0_endset:
                    for q in child1_startset:
                        combination1 = p + '->' + q
                        list_str1 = list()
                        list_str1.append(combination1)
                        loop_TarSet.update(list_str1)
                for k in child1_endset:
                    for f in child2_startset:
                        combination2 = k + '->' + f
                        list_str2 = list()
                        list_str2.append(combination2)
                        loop_TarSet.update(list_str2)
            else:
                for m in child0_endset:
                    for n in child1_startset:
                        combination3 = m + '->' + n
                        list_str3 = list()
                        list_str3.append(combination3)
                        loop_TarSet.update(list_str3)
        for z in range(len(nodeList)):
            str_nodelist = str(nodeList[z])
            child_tarset = get_tarSet_from_str(str_nodelist)
            loop_TarSet.update(child_tarset)
    return loop_TarSet
# print("loopTARSet---->",get_loop_TARSet(t(tree)))

#输入操作符及其孩子节点的列表，输出可替换该操作符节点的字符串
def replace_str_SE(operator1,xnode):
    str_SE = list()
    if operator1 == Operator.SEQUENCE:
        str_SE.append('SEQUENCE + StartSet:' + str(get_seq_StartSet(xnode)) + ' + EndSet:' + str(get_seq_EndSet(xnode)) + ' + TARSet:' + str(get_seq_TARSet(xnode)))
    elif operator1 == Operator.XOR:
        str_SE.append('XOR + StartSet:' + str(get_xor_StartSet(xnode)) + ' + EndSet:' + str(get_xor_EndSet(xnode)) + ' + TARSet:' + str(get_xor_TARSet(xnode)))
    elif operator1 == Operator.PARALLEL:
        str_SE.append('PARALLEL + StartSet:' + str(get_parallel_StartSet(xnode)) + ' + EndSet:' + str(get_parallel_EndSet(xnode)) + ' + TARSet:' + str(get_parallel_TARSet(xnode)))
    elif operator1 == Operator.LOOP:
        str_SE.append('LOOP + StartSet:' + str(get_loop_StartSet(xnode)) + ' + EndSet:' + str(get_loop_EndSet(xnode)) + ' + TARSet:' + str(get_loop_TARSet(xnode)))
    return str_SE

#输入节点，输出该节点改变后的样子
def Operator2Label(xnode):
    # print("当前xnode----》",xnode)
    dic0 = get_operator_child_dic(xnode)
    # print("dic0",dic0)
    for key,value in dic0.items():
        # print("key--->",key,"&value--->",value)
        x_label = replace_str_SE(key, value)
        # print("x_label================>",x_label)
        if(have_parent(xnode)):
            # print("yes!!!!!!!!!")
            x_parent = xnode._get_parent()
            # 创建一个新结点child_1，父节点设为x_parent
            child_1 = ProcessTree(children=None, label=str(x_label), parent=x_parent)
        else:
            child_1 = ProcessTree(children=None, label=str(x_label), parent=None, operator=None)
            xnode._set_label(str(x_label))

    return child_1



def add_se_node(pt):
    if pt.operator == Operator.SEQUENCE:
        se_tree = ProcessTree(operator=Operator.SEQUENCE)
        s_node = ProcessTree(parent=se_tree, children=None, label="start_node")
        e_node = ProcessTree(parent=se_tree, children=None, label="end_node")
        se_tree.children.append(s_node)
        for i in range(len(pt.children)):
            pt.children[i].parent = se_tree
            se_tree.children.append(pt.children[i])
        se_tree.children.append(e_node)
        return se_tree

    else:
        se_tree = ProcessTree(operator=Operator.SEQUENCE)
        s_node = ProcessTree(parent=se_tree, children=None, label="start_node")
        pt.parent =se_tree
        e_node = ProcessTree(parent=se_tree, children=None, label="end_node")
        se_tree.children.append(s_node)
        se_tree.children.append(pt)
        se_tree.children.append(e_node)
        return se_tree


#输入过程树，得到TAR集合
def get_PT_TARSet(ProcessTree0):
    ProcessTree0 = add_se_node(ProcessTree0)
    reduce_tau_leaf(ProcessTree0)
    # 树的高度
    deep = get_process_tree_height(ProcessTree0)

    while(deep >= 2):
        t_leaves1 = t(ProcessTree0)
        treelist2 = use_parent_classify_leaves(t_leaves1)
        for abc in range(len(treelist2)):
            # print("abc", abc, "+treelist2:", treelist2[abc])
            dic0 = get_operator_child_dic(treelist2[abc])
            leaf_position_dic = dict()
            for item in range(len(list(dic0.values())[0])):
                leaf = list(dic0.values())[0][item]
                position = item
                leaf_position_dic.update({leaf: position})
            nodesParent = list(dic0.values())[0][0]._get_parent()
            for item in range(len(list(dic0.values())[0])):
                if (contain_rename_node(list(dic0.values())[0][item]) == False):
                    newNode = LeafNode2Label(list(dic0.values())[0][item])
                    nodesParent.children[item] = newNode
                    continue;

            # print("list(dic0.values())[0][0]._get_parent()***************", list(dic0.values())[0][0]._get_parent())
            # for i in range(len(list(dic0.values())[0])):
            #     print("nodesParent.children[i]", nodesParent.children[i])

        for operatorTree in treelist2:
            if(operatorTree._get_parent() != None):
                operator_position_dic = dict()
                # print("len(operatorTree._get_parent().children)", len(operatorTree._get_parent().children))
                for yy in range(len(operatorTree._get_parent().children)):
                    opera = operatorTree._get_parent().children[yy]
                    opPosition = yy
                    operator_position_dic.update({opera: opPosition})
                newOpNode = Operator2Label(operatorTree)
                index = operator_position_dic.get(operatorTree)
                operatorTree._get_parent().children[index] = newOpNode
            else:
                Operator2Label(operatorTree)



        deep -= 1


    root_node = ProcessTree0._get_root()

    root_node_str = str(root_node._get_label())
    All_TARSet = set()
    All_TARSet.update(get_tarSet_from_str(root_node_str))
    return All_TARSet
