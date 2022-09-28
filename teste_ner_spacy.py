import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json
import glob
import pandas as pd
import re
from processador_trechos import processamento

def treino():

	nlp = spacy.blank("pt") # load a new spacy model
	db = DocBin() # create a DocBin object
	dados_excel = pd.DataFrame()
	colunas = []
	valores = []


	lista_json = glob.glob("./treino_v3/*.json")
	# print(len(lista_json))
	# z= input("")

	n= -1
	for dtb in lista_json:

		f = open(dtb, encoding="utf8")
		# print(f)
		TRAIN_DATA = json.load(f)
		# print("---------------------------")
		# print(dtb)

		for text, annot in tqdm(TRAIN_DATA['annotations']): 

			doc = nlp.make_doc(text)
			ents = []
			for start, end, label in annot["entities"]:
				span = doc.char_span(start, end, label=label, alignment_mode="contract")
				if span is None:
					print("Skipping entity")
				else:
					n = n+1
					ents.append(span)
					# print(span.label_)
					# print(label)
					# print(span)
					# print(ents)
					# print(type(span.orth_))
					# print(span.orth_)
					dados_excel.loc[n,label] = span.orth_
					# print(dados_excel)
					colunas.append(span.label_)
					valores.append(span.text)

				  	# z= input("")
			doc.ents = ents
			db.add(doc)
			# print("o DB agora tem",len(db))

	print(dados_excel)   
	dados_excel.to_excel("dados_treino_procuracoes.xlsx", index= False)
	# db.to_disk("./training_data_procuracoes.spacy") # save the docbin object


	############## IMPORTANTE ##############################


	# é preciso baixar o widget do spacy com o arquivo base_config escolhido a opção português e NER.

	# terminado esse processo é preciso setar no terminal primeiro com o comando:

	# python -m spacy init config config.cfg --lang pt --pipeline ner --optimize efficiency

	# or

	# python -m spacy init config config.cfg --lang pt --pipeline ner --optimize accuracy

	# depois com o comando

	# python -m spacy train config.cfg --output ./ --paths.train ./training_data_procuracoes.spacy --paths.dev ./training_data_procuracoes.spacy

	# com isso o sistema vai começar a treinar o modelo


####################################################################################################

def classificar_spacy(texto):

	nlp_ner = spacy.load("./model-best")

	doc = nlp_ner(texto)
	entidades = [entity.label_ for entity in doc.ents]
	trechos = [entity.text.strip().replace("\n"," ").replace("\r",' ').replace("\t",' ') for entity in doc.ents]
	

	df = pd.DataFrame()
	for entidade,trecho in zip(entidades, trechos):
		dic_df = {entidade: trecho} 
		df_prov = pd.DataFrame([dic_df])
		df = pd.concat([df,df_prov], ignore_index = True)
	
	# print(df)
	# z = input("")

	# taman = df.shape[1]
	
	vlr_final, nome = processamento(df)




	if nome == "procuração/substabelecimento" or nome == "petição inicial":
		# print("-"*20)
		# print("-"*20)
		# print()
		# print("100%% de certeza")
		# print()
		# print("-"*20)
		# print("-"*20)
		# print(texto)
		# print("-"*20)
		# print("-"*20)

		# z = input("")
		# print(df)
		# z= input("")
		return True,df,nome

	# elif nome == "petição inicial": # procuração 80%
		# print("-"*20)
		# print("-"*20)
		# print()
		# print("80%% de certeza")
		# print()
		# print("-"*20)
		# print("-"*20)
		# print(texto)
		# print("-"*20)
		# print("-"*20)	
		# z = input("")
		# print(df)
		# # z = input("")
		# return True,df,nome

	else:
		df = pd.DataFrame()
		return False, df, nome
	
	# return vlr_final


#####################################################################################################

if __name__ == "__main__":
	treino()
	# classificar()