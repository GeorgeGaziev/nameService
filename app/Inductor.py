import os
import pickle
import re
import numpy as np
import copy
import math


def process(data):

    newData = NotBruteAtAll(data.value)


    #
    # # 0 = все отлично, 1 = что-то поменяли, 2 = слишком редкое слово, 3 = странный пол, 4 = слова нет в базах."
    # markerInfo = {
    #     0: ["Без изменений", (33, 128, 54)],  # green
    #     1: ["Замена", (255, 255, 0)],  # yellow
    #     2: ["Редкое слово", (154, 205, 50)],  # yellow-green
    #     3: ["Несовпадение пола", (255, 165, 0)],  # orange
    #     4: ["Слово не найдено", (255, 0, 0)],  # red
    #     5: ["Возникло несколько ошибок", (255, 0, 0)]
    # }
    #
    # RowCounter = 1
    # for result in newData:
    #
    #     marker = []
    #
    #     for res in result[1]:
    #         if type(res)==int:
    #             marker.append(res)
    #         else:
    #             marker.append(res[0])
    #
    #     currentSheet.range('A' + str(RowCounter)).value = result[0]
    #     if len(marker) == 1:
    #         # один результат
    #         currentSheet.range('B' + str(RowCounter)).color = markerInfo[marker[0]][1]
    #         currentSheet.range('B' + str(RowCounter)).value = markerInfo[marker[0]][0]
    #         if marker[0] == 1:
    #             currentSheet.range('C' + str(RowCounter)).value = "\"" + result[1][0][1].title() + "\" на \"" + result[1][0][2].title() + "\""
    #         else:
    #             currentSheet.range('C' + str(RowCounter)).value = result[1][0][1].title()
    #
    #     else:
    #         # несколько результатов
    #         currentSheet.range('B' + str(RowCounter)).color = markerInfo[5][1]
    #         currentSheet.range('B' + str(RowCounter)).value = markerInfo[5][0]
    #         info = ""
    #         for res in result[1]:
    #             if res[0] == 1:
    #                 info = info + markerInfo[res[0]][0] + ": \"" + res[1].title() + "\" на \"" + res[2].title() + "\";"
    #             elif res[0] == 3:
    #                 info = info + markerInfo[res[0]][0] + ";"
    #             else:
    #                 info = info + markerInfo[res[0]][0] + ": "+ res[1].title() + ";"
    #         currentSheet.range('C' + str(RowCounter)).value = info
    #     RowCounter += 1
    # currentSheet.autofit()


# Используемые константы

pathDirectory = os.path.dirname(os.path.realpath(__file__)) + "/Data/"  # Путь к папке, где хранятся все базы

roundFactorDefiningAfterStrict = 5
# Перед проверкой нечетким поиском, мы определяем можем ли мы что-то определить после строгой проверки
# Для этого сравниваем все результаты, считая что если значение в 10**n раз меньше чем максимум, то сичитать его нулем, не учитывать

allowedDistanceInDamerauCheck = 1
# Максимальное расстояние между проверяемым словом и словом в словаре при проверке нечетким поиском
# + можно сделать отдельное для каждого типа части речи (+возможно потом рассчитывать его еще учитывая длину слова)
# Раньше значение было 2, но слишком много влезало ненужных фамилий

statisticsFactor = 0.00005
# Коэффициент влияния статистики на результат

roundAproximationForRecursionStart = 5
# Начальная степень округления для проверки рекурсией

roundAproximationForRecursionEnd = 1
# Конечная степень округления для проверки рекурсией (меньше не округлять)

maxDistanceInReplaceCheck = 1
# Максимальная разница длин исходного слова и слова в списке при нечетком поиске

probabilityForFoundWordsInReplace = 1
# Коэффициент, во сколько раз уменьшается вероятность слова, при нахождении его в нечетком поиске

# Стоимость соответсвующего действия в подсчете расстояния Дамерау-Левенштейна
damerauDeleteCost = 1
damerauInsertCost = 1
damerauReplaceCost = 1
damerauTransposeCost = 1

grammaFactor = 0.0000001
# Коэффициент влияния проверки по грамматике на результат

grammaSurnameFactor = 0.0001
# Коэффициент влияния проверки фамилии по грамматике на результат
# (т.к. многие фамилии отсутствуют в базе, данный коэффициент имеет такой большой вес)

grammaPatronymicFactor = 0  # .00001
# Коэффициент влияния проверки отчества по грамматике на результат

qualityCheck = 0.0000001


# Если частота слова меньше заданной, то оно считается подозрительно редким


# In[4]:
def ProcessSingle(text):
    res = []
    text = text.lower()
    words = text.split(" ")
    # +добавить здесь некую предобработку вводимой строки - удалить лишние пробелы, изменить е-ё и т.д.
    # +обработка фамильных приставок (фон, оглы ...), не рассматривать их как отдельное слово
    result, order, qualityFlag = WordsProcessing(words)
    SetStatistics(order)  # обновляем статистику
    # gender = CheckGender(result) #получаем пол, исходя из результата
    #
    # вывод результата в виде строки
    output = ""
    for r in result:
        for w in r:
            output += w.title() + " "
    return output.strip()
    # qualityResult = [0, ""]
    # if len(qualityFlag) > 1 and qualityResult in qualityFlag:
    #     qualityFlag.remove(qualityResult)
    # res.append([output, qualityFlag])
    # print(res)
    # return res

def NotBruteAtAll(temp):
    res = []
    for t in temp:
        t = t.lower()
        words = t.split(" ")

        # +добавить здесь некую предобработку вводимой строки - удалить лишние пробелы, изменить е-ё и т.д.
        # +обработка фамильных приставок (фон, оглы ...), не рассматривать их как отдельное слово

        result, order, qualityFlag = WordsProcessing(words)

        SetStatistics(order)  # обновляем статистику
        # gender = CheckGender(result) #получаем пол, исходя из результата
        #
        # вывод результата в виде строки
        output = ""
        for r in result:
            for w in r:
                output += w.title() + " "
        output = output.strip()
        qualityResult = [0,""]
        if len(qualityFlag)>1 and qualityResult in qualityFlag:
            qualityFlag.remove(qualityResult)
        res.append([output, qualityFlag])
    return res


# In[42]:


def WordsProcessing(words):
    qualityFlag = []
    N = len(words)  # Количество слов

    # Создаем массив для записи результатов
    # Результат хранится в виде: [[фамилия1,фамилия2...],[имя1,имя2...],[отчество1,отчество2...]]
    result = []
    for i in range(3):
        result.append([])

    # Создаем массив для записи порядка
    # Порядок хранится в виде массива, где каждому введенному слову сопоставляется номер значения(0 = фамилия, 1 = имя, 2 = отчество)
    # Для Иван Иванович Сидоров порядок будет [1,2,0] (т.е. порядок имя, отчество, фамилия)
    order = []
    for i in range(N):
        order.append(None)

    resultStrict = StrictCheck(words)  # матрица с вероятностями после строгой проверки

    # Теперь когда у нас база отчеств полная, используем проверку по грамматике только после, когда не прошла строгая проверка

    recurMatrix = RecursiveProcessing(
        copy.deepcopy(resultStrict))  # проводится обработка матрицы (выбираются очевидные варианты)
    check = СheckMatrix(
        recurMatrix)  # проверяем можем ли мы однозначно определить все слова (в строке по одному значению)

    if check:
        order = GetOrder(recurMatrix)  # определяем порядок слов и записываем их в результат
        qualityFlag.append([0, ""])
        for i in range(N):
            result[order[i]].append(words[i])
        for i in range(N):
            if words[i] in bases[order[i]]:
                if (bases[order[i]][words[i]]<qualityCheck):
                    qualityFlag.append([2,words[i]]) #редкое слово
    else:
        resultGramma = GrammaCheck(
            words)  # матрица с вероятностями после проверки по грамматике (окончания фамилий и отчеств)
        # Суммируем полученные значения
        # результат по грамматике учитывается только в случае если данное слово нигде не найдено
        # вынужденый шаг, чтобы помогать определить фамилии которых нет в базе, но при этом не мешать остальным значениям
        for i in range(N):
            if resultStrict[i].count(0) == 3:
                for j in range(3):
                    resultStrict[i][j] += resultGramma[i][j]

        replaceWords = []  # матрица для слов, полученных в результате нечеткого поиска
        replaceValues = []  # матрица вероятностей, соответсвующих словам из нечеткого поиска
        for i in range(N):
            replaceWords.append([words[i], words[i], words[i]])
            replaceValues.append([0, 0, 0])

        # Проверяем можем ли мы с уверенностью что-то определить
        # Для этого если вероятность одного значения в столбце значительно больше остальных мы его запоминаем.
        # +возможно вставить вместо этого метод round
        for j in range(3):
            temp = []
            for i in range(N):
                temp.append(resultStrict[i][j])
            indexMax = temp.index(max(temp))
            f = True
            for i in range(N):
                if i != indexMax and resultStrict[i][j] * 10 ** roundFactorDefiningAfterStrict >= \
                        resultStrict[indexMax][j]:
                    f = False
            if f:
                order[indexMax] = j

                # Оставшиеся слова, не определенные в строгой проверке, проверяем через расстояние между словами
        for i in range(N):
            if order[i] is None:
                for j in range(3):
                    wordRepl, valueRepl = forReplaceCheck(words[i], bases[j], allowedDistanceInDamerauCheck)
                    if wordRepl != "":
                        replaceWords[i][j], replaceValues[i][j] = wordRepl, valueRepl

        # +добавить сюда проверку, если ничего не было найдено через расстояние, то не выполнять суммирование значений
        # Суммируем полученные значения
        resForNow = []
        for i in range(N):
            resForNow.append([0, 0, 0])
        for i in range(N):
            for j in range(3):
                if resultStrict[i][j] > replaceValues[i][j]:
                    resForNow[i][j] = resultStrict[i][j]
                    replaceWords[i][j] = words[i]
                else:
                    resForNow[i][j] = replaceValues[i][j]

        # Если у нас существует статистика для введенного количества слов, учитываем её
        if N <= 4:
            for i in range(N):
                for j in range(3):
                    resForNow[i][j] += statisticsFactor * statistics[N - 1][i][j]

        # Анализируем полученную матрицу
        order = ComplexOrder(resForNow, order)

        # Исходя из порядка, записываем результат
        for i in range(N):
            result[order[i]].append(replaceWords[i][order[i]])

        # Значения qualityFlag: 0 = все отлично, 1 = что-то поменяли, 2 = слишком редкое слово, 3 = странный пол, 4 = слова нет в базах.
        for i in range(N):
            if replaceWords[i][order[i]] in bases[order[i]]:
                if (bases[order[i]][replaceWords[i][order[i]]] < qualityCheck):
                    qualityFlag.append([2, replaceWords[i][order[i]]])  # редкое слово
            if replaceWords[i][order[i]] not in bases[order[i]]:
                qualityFlag.append([4, replaceWords[i][order[i]]])  # слово которого нет в базах
            if replaceWords[i][order[i]] not in words:
                qualityFlag.append([1, words[i], replaceWords[i][order[i]]])  # слово на которое поменяли

    gender = CheckGender(result)  # получаем пол, исходя из результата
    # Если пол с ошибкой, т.е. Петров Анна, значит что-то подозрительное
    if gender == genderTuple[3]:
        qualityFlag.append([3, ""])
        # Значения qualityFlag: 0 = все отлично, 1 = что-то поменяли, 2 = слишком редкое слово, 3 = странный пол, 4 = слова нет в базах.

    return result, order, qualityFlag  # + probability + добавить разные варинаты результата


# In[7]:


def RecursiveProcessing(matrix, matrixOld=None, flag=False, aproximation=roundAproximationForRecursionStart):
    # Рекурсивное изменение значений в матрице - преобразует матрицу
    #  F  I  O               ` F  I  O
    # [[1,0,1],                [[0,0,1],
    #  [1,1,1],     в матрицу   [0,1,0],
    #  [1,0,0]]                 [1,0,0]]
    # Т.е. выбирает очевидные варианты

    # matrixOld - значение матрицы в предыдущей итерации. Если никаких изменений не было произведено, метод завершается
    # flag - нужно или не нужно использовать округление значений матрицы
    # aproximation - степень округления

    # Если никаких изменений не было произведено, или степень оркгуления достигла минимума, метод завершается
    if (matrix == matrixOld and not flag) or (aproximation == roundAproximationForRecursionEnd and flag):
        return matrix

        # Сохраняется текущее значение матрицы, для сравнения в следующей итерации
    matrixOld = copy.deepcopy(matrix)
    N = len(matrix)

    # Подсчитывается количество ненулевых элементов в каждом столбце
    countersColumns = []
    for j in range(3):
        countersColumns.append(0)
        for i in range(N):
            if matrix[i][j] != 0: countersColumns[j] += 1

    # Подсчитывается количество ненулевых элементов в каждой строке
    countersRows = []
    for i in range(N):
        countersRows.append(0)
        for j in range(3):
            if matrix[i][j] != 0: countersRows[i] += 1

    # Если в каждой строке по одному значению, следовательно желаемое было достигнуто, найдены все слова
    if countersRows.count(1) == N:
        return matrix
        # + добавить проверку значений по столбцам np.array(countersColumns).sum()==N или all(element in countersColumns == N)
    else:
        # Если есть один элемент, который является единственным в своем столбце, то обнуляются лишние элементы в его строке
        # [[0,0,1],    [[0,0,1],
        #  [1,1,1], ->  [0,1,0],
        #  [1,0,0]]     [1,0,0]]
        for j in range(3):
            if countersColumns[j] == 1:
                m = -1
                for i in range(N):
                    if matrix[i][j] != 0:
                        m = i
                        break
                if m > -1:
                    for k in range(3):
                        # элементы обнуляются с условием - если они в свою очередь не являются единственными в своем столбце
                        if k != j and countersColumns[k] > 1:
                            matrix[m][k] = 0

        # Проводится то же самое что и перед этим, но уже для строк а не столбцов
        for i in range(N):
            if countersRows[i] == 1:
                for j in range(3):
                    m = -1
                    if matrix[i][j] != 0:
                        m = j
                        break
                    if m > -1:
                        for k in range(N):
                            if k != i and countersRows[k] > 1:
                                matrix[k][m] = 0

                                # Если необходимо выполнение метода с округлением элементов, то оно выполняется,
        # и при последующем вызове метода, коэффициент округления будет меньше на единицу
        # +возможно вызывать его не здесь, а только при условии что не происходит никаких изменений в методе
        if flag:
            RoundMatrix(matrix, aproximation)
        return RecursiveProcessing(matrix, matrixOld, flag, aproximation - 1)


# In[8]:


def ComplexOrder(matrix, order):
    # +ещё подредактировать этот метод

    # Из матрицы исключаются элементы, уже определенные в order
    ExcludeDefined(matrix, order)

    # проверяем можем ли мы однозначно определить все слова (в строке по одному значению)
    if СheckMatrix(matrix):
        return GetOrder(matrix)

    N = len(matrix)

    # Создаем массивы с индексами максимальных элементов по строкам и столбцам
    maxRows = []
    maxColumns = [0, 0, 0]
    for i in range(N):
        maxRows.append(0)

    for i in range(N):
        for j in range(3):
            if matrix[i][j] > matrix[i][maxRows[i]]:
                maxRows[i] = j

    for j in range(3):
        for i in range(N):
            if matrix[i][j] > matrix[maxColumns[j]][j]:
                maxColumns[j] = i

    # Если элемент максимален и в своей строке и в своем столбце, то считаем это значение правильным
    for i in range(N):
        for j in range(3):
            if maxRows[i] == j and maxColumns[j] == i:
                if order[i] == None:
                    order[i] = maxRows[i]

    # Подсчитываем количество определенных элементов
    # +возможно переместить этот блок ниже, после RecursiveProcessing
    n = order.count(None)
    if n == 0:
        return order
    elif n <= N - 2:
        # Если определено достаточное количетсво элементов, то оставшиеся мы можем определить методом исключения
        k = 0  # Количество неопределенных частей имени
        num = 0
        for j in range(3):
            if j not in order:
                k += 1
                num = j
        # Если не определена только одна, то можно предположить, что её и следует сопоставить оставшемуся слову
        # Сопоставляется только в случае если его вероятность не равна 0
        if k == 1:
            for i in range(N):
                if order[i] == None and matrix[i][num] > 0:
                    order[i] = num
        if order.count(None) == 0: return order

        # Попытка выполнения предыдущей части, но определять необходимое количество элементов в столбце исходя из количества слов
        # +еще будут доработки
        for i in range(N):
            for j in range(3):
                if order[i] == None and order.count(j) <= N - 3:
                    order[i] = j

    # Исключаем опредленные элементы
    ExcludeDefined(matrix, order)
    # Выполняем проверку рекурсивным алгоритмом применяя округление
    matrix = RecursiveProcessing(matrix, None, True)
    # +добавить сюда СheckMatrix? А если не совпадает, прогонять по методу заново...
    return GetComplexOrder(matrix, order)


# In[9]:


def ExcludeDefined(matrix, order):
    # Исключаются элементы матрицы, которые уже определены в order
    # Делается это с помощью обнуления больше не нужных элементов в строке уже определенного элемента
    for i in range(len(matrix)):
        if order[i] != None:
            for j in range(3):
                if order[i] != j:
                    matrix[i][j] = 0


# In[10]:


def RoundMatrix(matrix, n):
    # Производится округление матрицы с приблежением n
    # Под округлением понимается: если значения элементов строки/столбца меньше значения максимального элемента в 10**n раз,
    # то их можно считать несущественными и округлить до нуля
    N = len(matrix)
    for i in range(N):
        for j in range(3):
            if matrix[i][j] * 10 ** n < max(matrix[i]):
                matrix[i][j] = 0
    maxColumns = [0, 0, 0]
    for j in range(3):
        for i in range(N):
            if matrix[i][j] > matrix[maxColumns[j]][j]:
                maxColumns[j] = i

    for j in range(3):
        for i in range(N):
            if matrix[i][j] * 10 ** n < matrix[maxColumns[j]][j]:
                matrix[i][j] = 0


# In[11]:


def GetOrder(matrix):
    # Определяет порядок элементов по матрице, исходя из гипотезы что в ней по одному элементу на строку
    N = len(matrix)
    order = []
    for i in range(N):
        order.append(None)
        for j in range(3):
            if matrix[i][j] != 0:
                order[i] = j
                break
    return order


# In[12]:


def GetComplexOrder(matrix, order):
    # Грубое определение порядка элементов по матрице
    # +потом реализовать по другому
    N = len(matrix)
    for i in range(N):
        if order[i] == None:
            for j in range(3):
                if matrix[i][j] != 0:
                    order[i] = j
                    break
    return order


# In[13]:


def СheckMatrix(matrix):
    # Проверяет матрицу: если в ней в одной строке по одному элементу, возвращает True
    N = len(matrix)
    for i in range(N):
        k = 0
        for j in range(3):
            if (matrix[i][j] != 0): k += 1
        if (k != 1):
            return False
    return True


# In[14]:


def StrictCheck(words):
    # Строгая проверка
    N = len(words)
    result = []
    for i in range(N):
        result.append([0, 0, 0])
        w = words[i].strip()
        for j in range(3):
            if w in bases[j]:
                result[i][j] = bases[j][w]
    return result


# In[15]:


def forReplaceCheck(w, list, mistakes=allowedDistanceInDamerauCheck):
    # Нечеткая проверка
    # Ищет в list слова с расстоянием mistakes до исходного слова w

    # Список словарей. В каждом словаре найденные слова с одинаковым расстоянием (в словаре res[0] - слова с расстоянием 1 и т.д.)
    # +пока сделано так, т.к. обсуждали такую реализацию на семинаре, возможно потом отказаться, и сделать общий словарь
    res = []
    for i in range(mistakes):
        res.append({"": 0})

    # для каждого слова в списке выполняется проверка
    for l in list:
        dist = False
        # если разница длин исходного слова и слова в списке больше чем заданная в константе, то проверка расстояния не выполняется
        if math.fabs(len(l) - len(w)) <= maxDistanceInReplaceCheck:
            # dist = levenshtein(word, dictWord)
            dist = damerau(w, l)  # Подсчет расстояния
            if (dist > mistakes):  # Сравнение полученного расстояния с допустимым
                dist = False
        if (dist != False):
            res[int(dist) - 1][l] = list[l] * 10 ** (-probabilityForFoundWordsInReplace * dist)
            # Найденное слово и его вероятность добавляются в соответсвующий словарь
            # при этом его вероятность уменьшается в 10**(probabilityForFoundWordsInReplace*dist) раз,
            # т.е. в зависимости от расстояния будет разниться и вероятность (больше расстояние - меньше вероятность)

    # Выбираются максимальные вероятности и слова, им соответсвующие, по каждому словарю
    # +опять же, как было сказано ранее, можно будет это убрать, и сделать общий словарь
    keys = []
    values = []
    for i in range(mistakes):
        keys.append("")
        values.append(0)
        keys[i], values[i] = max(res[i].items(), key=lambda x: x[1])
    # Затем они сравниваются между собой, и метод возвращает слово с максимальной вероятностью
    iMax = 0
    for i in range(mistakes):
        if values[i] > values[iMax]: iMax = i
    return keys[iMax], values[iMax]


# In[16]:


def levenshtein(s, t):  # подсчет расстояние Левенштейна (сейчас не используется)
    if s == t:
        return 0
    elif len(s) == 0:
        return len(t)
    elif len(t) == 0:
        return len(s)
    v0 = [None] * (len(t) + 1)
    v1 = [None] * (len(t) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]
    return v1[len(t)]


# In[17]:


def damerau(s, t):  # расстояние Дамерау-Левенштейна (расстояние с перестановкой)
    if s == t:
        return 0
    elif len(s) == 0:
        return len(t)
    elif len(t) == 0:
        return len(s)

    deleteCost = damerauDeleteCost
    insertCost = damerauInsertCost
    replaceCost = damerauReplaceCost
    transposeCost = damerauTransposeCost

    s = " " + s
    t = " " + t
    M = len(s)
    N = len(t)
    d = [list(range(N))]
    for i in range(1, M):
        d.append([])
        for j in range(N):
            d[i].append(0)
        d[i][0] = i

    for i in range(1, M):
        for j in range(1, N):
            # Стоимость замены
            if (s[i] == t[j]):
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = d[i - 1][j - 1] + replaceCost
            d[i][j] = min(
                d[i][j],  # замена
                d[i - 1][j] + deleteCost,  # удаление
                d[i][j - 1] + insertCost  # вставка
            )
            if (i > 1 and j > 1 and s[i] == t[j - 1] and s[i - 1] == t[j]):
                d[i][j] = min(
                    d[i][j],
                    d[i - 2][j - 2] + transposeCost  # транспозиция
                )
    return d[M - 1][N - 1]


# In[18]:


def GrammaCheck(words):
    # Проверка по грамматике - проверяются окончания отчества и фамилии
    # и возвращается матрица с элементами домноженными на соответсвующие коэффициенты
    # +возможно добавить разные веса для разных окончаний (частых и более редких)

    N = len(words)
    grammaRes = []
    for i in range(N):
        grammaRes.append([0, 0, 0])
        w = words[i]
        grammaRes[i][0] = checkSurnames(w) * grammaFactor * grammaSurnameFactor
        grammaRes[i][2] = checkPatronymic(w) * grammaFactor * grammaPatronymicFactor
    return grammaRes
    # Пока не используется:
    # для определения имени нет метода, но можно заполнять по методу исключения:
    # if flag:
    #     #По принципу исключения заполняет вероятности имен
    #     k = 0
    #     for i in range(N):
    #         flag = True
    #         for j in range(3):
    #             if (result[i][j] != 0):
    #                 flag = False
    #                 break
    #         if(flag):
    #             result[i][1] = 1
    #             k+=1
    #     if(k==0):
    #         for i in range(N): result[i][1] = 0.001*0.30
    #     elif(k>1):
    #         for i in range(N): result[i][1] = 0.001*result[i][1]*0,9/k
    #
    # return result


# In[19]:


def checkSurnames(s):
    # Проверка окончаний фамилий
    pattern = '\w*(ов|ова|ев|ёв|ева|ёва|ив|ин|ина|ын|их|ых|ский|цкий|ая|ко|дзе'               '|онок|ян|ен|ук|юк|ун|ний|ный|чай|ий|ич|ов|ук|ик|цки|дзки|ан)$'

    if (re.match(pattern, s)):
        return 1
    else:
        return 0


# In[20]:


def checkPatronymic(s):
    # Проверка окончаний отчеств
    pattern = '\w*(ович|евич|ич|овна|евна|ична|инична)$'
    if (re.match(pattern, s)):
        return 1
    else:
        return 0


# In[21]:


# Матрицы значения статистики порядка слов
# пока что значения взяты очень приблизительные
#               F     I    O
statistics1 = [[0.45, 0.40, 0.15]]
#               F     I    O
statistics2 = [[0.50, 0.45, 0.05],
               [0.30, 0.30, 0.30]]
#               F     I    O
statistics3 = [[0.50, 0.45, 0.05],
               [0.10, 0.50, 0.40],
               [0.40, 0.05, 0.55]]
#               F     I    O
statistics4 = [[0.30, 0.15, 0.05],
               [0.30, 0.40, 0.30],
               [0.20, 0.40, 0.30],
               [0.20, 0.05, 0.35]]

statistics = [statistics1, statistics2, statistics3, statistics4]


def SetStatistics(order):
    # Метод обновляет статистику с учетом результата выполнения алгоритма
    N = len(order)
    if N <= 4:
        for i in range(N):
            for j in range(3):
                if (j == order[i]):
                    statistics[N - 1][i][j] += 0.002
                else:
                    statistics[N - 1][i][j] -= 0.001


# In[22]:


genderTuple = ('.', 'М', 'Ж', 'Несоответствие')  # массив значений пола


# In[23]:


def CheckGender(result):
    # Метод определения пола по результату
    genderResult = [[], [], []]
    methods = [checkSurnamesGender, lambda s: 0, checkPatronymicGender]

    for i in range(3):
        for r in result[i]:
            if i != 0 and r in basesFull[i]:
                genderResult[i].append(genderTuple.index(basesFull[i][r][0]))
            else:
                genderResult[i].append(methods[i](r))

    index = 0
    for i in range(3):
        for j in range(len(genderResult[i])):
            if index == genderResult[i][j] or index == 0:
                index = genderResult[i][j]
            elif index != genderResult[i][j] and genderResult[i][j] != 0:
                index = 3
                return genderTuple[index]
    return genderTuple[index]


# In[24]:


def checkSurnamesGender(s):
    # Проверяет пол исходя из окончания фамилии
    patternMale = '\w*(ов|ев|ий|ын|ин)$'
    patternFem = '\w*(ова|ева|ая|ина|ына)$'
    patternUnknown = '\w*(их|ых|ко|ук|юк|ун|ний|ный|чай|ий|а|ич|ов|ук|ик|ски|ка|ски|цки|дзки)$'

    # + потом сделать в цикле
    if (re.match(patternMale, s)):
        return 1
        # return genderTuple[1]
    elif (re.match(patternFem, s)):
        return 2
        # return genderTuple[2]
    elif (re.match(patternUnknown, s)):
        return 0
        # return genderTuple[0]
    else:
        return 0
        # return genderTuple[0] #Можно сделать другой вывод


# In[25]:


def checkPatronymicGender(s):
    # Проверяет пол исходя из окончания отчества
    # +можно вместо этого просто сделать проверку оканчивается ли на "а" или нет
    patternMale = '\w*(ович|евич|ич)$'
    patternFem = '\w*(овна|евна|ична|инична)$'

    if (re.match(patternMale, s)):
        return 1
    elif (re.match(patternFem, s)):
        return 2
    else:
        return 0


# In[26]:


# Работа с базами, загрузка и обработка
surnames = {}
names = {}
patronymics = {}

path_to_surnames = pathDirectory + "all_surnames.pickle"
path_to_names = pathDirectory + "all_names.pickle"
path_to_patronymics = pathDirectory + "all_patronymics.pickle"
with open(path_to_surnames, "rb") as f:
    surnames = pickle.load(f)
with open(path_to_names, "rb") as f:
    names = pickle.load(f)
with open(path_to_patronymics, "rb") as f:
    patronymics = pickle.load(f)

# Временные меры, пока мы не приведем базы к конечной форме, чтобы не изменять код каждый раз в зависимости от изменения структуры
all_surnames = {}
all_names = {}
all_patronymics = {}
for s in surnames:
    all_surnames[s] = surnames[s][1]
for s in names:
    all_names[s] = names[s][2]
for s in patronymics:
    all_patronymics[s] = patronymics[s][2]

bases = [all_surnames, all_names, all_patronymics]
basesFull = [surnames, names, patronymics]


# In[27]:


# старый модуль с полами, не используется

# genderTuple = ('male', 'female', 'unknown') #Неизменяемый массив значений пола
#
# def checkSurnamesGender(s):
#     #Проверяет пол исходя из окончания фамилии
#     patternMale = '\w*(ов|ев|ий|ын|ин)$'
#     patternFem ='\w*(ова|ева|ая|ина|ына)$'
#     patternUnknown = '\w*(их|ых|ко|ук|юк|ун|ний|ный|чай|ий|а|ич|ов|ук|ик|ски|ка|ски|цки|дзки)$'
#
#     if (re.match(patternMale,s)):
#         return genderTuple[0]
#     elif (re.match(patternFem,s)):
#         return genderTuple[1]
#     elif (re.match(patternUnknown,s)):
#         return genderTuple[2]
#     else: return genderTuple[2] #Можно сделать другой вывод

def changeGenderSurname(s):
    # Меняет пол фамилии
    patternMaleA = '\w*(ов|ев|ин|ын)$'
    patternFemA = '\w*(ова|ева|ина|ына)$'
    patternMaleB = '\w*(ий)$'
    patternFemB = '\w*(ая)$'

    if (re.match(patternMaleA, s)):
        return s + 'a'
    elif (re.match(patternMaleB, s)):
        s += ' '
        return s.replace('ий ', 'ая')
    elif (re.match(patternFemA, s)):
        return s[0: len(s) - 1]
    elif (re.match(patternFemB, s)):
        s += ' '
        return s.replace('ая ', 'ий')
    else:
        return s


#
# def checkPatronymicGender(s):
#     #Проверяет пол исходя из окончания отчества
#     patternMale = '\w*(ович|евич|ич)$'
#     patternFem ='\w*(овна|евна|ична|инична)$'
#
#     if (re.match(patternMale,s)):
#         return genderTuple[0]
#     elif (re.match(patternFem,s)):
#         return genderTuple[1]
#     else: return 'No'

def changeGenderPatronymic(s):
    # Меняет пол отчества
    patternMaleA = '\w*(ович|евич)$'
    patternFemA = '\w*(овна|евна)$'
    patternMaleB = '\w*(ич)$'
    patternFemB = '\w*(ична|инична)$'

    if (re.match(patternMaleA, s)):
        s += ' '
        return s.replace('ич ', 'на')
    if (re.match(patternFemA, s)):
        s += ' '
        return s.replace('на ', 'ич')
    if (re.match(patternMaleB, s)):
        return s + 'на'
    if (re.match(patternFemB, s)):
        s += ' '
        s = s.replace('инична ', 'ич')
        s = s.replace('ична ', 'ич')
        return s
    else:
        return s

if __name__ == '__main__':
    ProcessSingle()