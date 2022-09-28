import nltk
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter
from nltk.corpus import stopwords
import gensim
import numpy as np
import os,re
import pandas as pd
from nltk.stem import PorterStemmer
import jellyfish
from nltk.stem import SnowballStemmer


def forma_tuplas_stem(df):

	taman = df.shape[1]

	df_final = pd.DataFrame()
	colunas = list(df.columns)
	# print(colunas)
	# z= input("")


	for b in range(len(colunas)):
		todos_stem =[]
		for a in range(len(df)):
			trecho = df.iloc[a,b]
			# print(colunas[b])
			if str(trecho) != "nan":
				trecho = trecho.lower()
				todos_stem.append(trecho)

				tokens = nltk.word_tokenize(trecho)
				tokens_unif = " ".join(tokens)
				todos_stem.append(tokens_unif)
			
				# rom_stemmer = SnowballStemmer('portuguese')


				# list_stem = []
				# for tk in tokens:
				# 	word_stem = rom_stemmer.stem(tk)
				# 	list_stem.append(word_stem)
				# # print(list_stem)
				# list_stem = " ".join(list_stem)
				# todos_stem.append(list_stem)
				# z = input("")
				
		df_final[colunas[b]] = pd.Series(todos_stem)
		# print(df_final)
		# z= input("")

	# print(df_final)	
	return df_final


#########################################################################

def compara_trechos_sub_proc(df1, df2):

	colunas_df1 = list(df1.columns)
	colunas_df2 = list(df2.columns)
	texto_only = re.compile("[^A-Za-z\s]")

	contagem_matches = 0
	colunas_match = []

	for col in colunas_df1:
		for colmn in colunas_df2:
			if col == colmn:
				data1 = df1[col]
				data2 = df2[colmn]
				# trechos_treino = {str_stem:index for str_stem in data2.iloc[:, 0].to_list()}
				# print(col)
				# print(data1)
				# print(data2)
				# z= input("")
				for n in range(len(data1)):
					stem_verif = data1.iloc[n]
					if str(stem_verif) != "nan":
						stem_verif = re.sub(texto_only, "", stem_verif)
						for j in range(len(data2)):
							stem_treino = data2.iloc[j]
							if str(stem_treino) != "nan":
								stem_treino = re.sub(texto_only, "", stem_treino)
								vlr = jellyfish.jaro_distance(stem_verif, stem_treino)
								if vlr > 0.7:
									# print(stem_treino,"=",stem_verif,"na coluna",col,"com o valor",vlr)
									# contagem_matches = contagem_matches+1
									if col not in colunas_match:
										colunas_match.append(col)
									# print("-----------------------------------")
									break
								# else:
									# print(stem_treino,"!=",stem_verif,"na coluna",col,"com o valor",vlr)


	# print(contagem_matches)
	# if "OAB" in colunas_match:
	# 	print("temos",len(colunas_match),"variaveis nesse documento")
	# 	print("-"*20)		
	# 	return len(colunas_match)
	# else:
	# 	return 0
	# print("temos",len(colunas_match),"variaveis nesse documento")
	# print("-"*20)		
	return len(colunas_match)


############################################################################

# def compara_trechos_peticao(df1, df2):

## fazer essa função


############################################################################

def processamento(df):

	planilha_treino = pd.read_excel("dados_treino_procuracoes.xlsx")

	df_entidades = forma_tuplas_stem(df)
	try:
		df_entidades.drop(columns="documento", inplace=True)
	except:
		pass

	df_treino = forma_tuplas_stem(planilha_treino)

	vlr_final = compara_trechos_sub_proc(df_entidades, df_treino)
	if 9 <= vlr_final >= 13:
		nome = "procuração/substabelecimento"
		return vlr_final, nome


	##############################
		
	# comentar essa parte depois de fazer a função

	else:
		nome = "nada"
		return vlr_final, nome

	##############################



	#### descomentar depois de fazer a função da petição ######	

	# else:
	# 	vlr_final = compara_trechos_peticao(df1, df2)
	# 	if "9" <= vlr_final >= "13":
			# nome =  "petição inicial"
	# 		return vlr_final, nome
	# 	else:
	# 		return -1, "nada"




##############################################################


def sep_representante(public):

	rgx_estad = "(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO|DP)"

	# limpar o texto do ponto para separar melhor o número da OAB
	text_ajust = public.replace(".","")
	text_ajust = text_ajust.replace("\n","")
	# print(text_ajust)


	oabs = []
	# print(public)

	oab_compile = re.compile("\d{3,10}(?:[A-Z]/|/.|/|[A-Z]/.)[A-Z][A-Z]")
	oab_comp = oab_compile.findall(text_ajust)
	# print(len(oab_comp))
	# z=input("")
	if len(oab_comp) > 0:
		for item in oab_comp:
			oabs.append(item)
	else:
		partes = re.split("oab",text_ajust, flags=re.IGNORECASE)[1:]
		# print(partes)
		# z=input("")
		for item in partes:
			item = item.strip()
			try:
				# print("o item é:\n",item[:10],"\n ***************")
				num_oab = re.findall('\d{3,10}',item[:14])
				estado_oab = re.findall(rgx_estad,item[:14])
				# print("a OAB é:",num_oab,"\nE o Estado é:",estado_oab,"\n ----------------")
				oabs.append(str(num_oab[0]+"/"+estado_oab[0]))
			except:
				try:
					# print("o item é:\n",item[:],"\n ***************")
					num_oab = re.findall('\d{3,10}',item[:])
					estado_oab = re.findall(rgx_estad,item[:])
					# print("a OAB é:",num_oab,"\nE o Estado é:",estado_oab,"\n ----------------")		
					oabs.append(str(num_oab[0]+"/"+estado_oab[0]))
				except:
					pass
	

	# print(oabs)
	return oabs


	################################################################################

if __name__ == "__main__":
	path = input("insira o path do DF em excel:")
	planilha_teste = pd.read_excel(path)
	planilha_teste.drop(columns="documento", inplace=True)
	processamento(planilha_teste)