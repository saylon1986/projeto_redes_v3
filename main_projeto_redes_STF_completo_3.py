import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path
import textract
from pathlib import Path
import fitz
import re
import os
import pandas as pd
import chardet
import shutil
import time
from teste_ner_spacy import classificar_spacy
# from verificador_similaridade import classificar
from processador_trechos import sep_representante


###########################################################################

# função principal

def Main():

	try:
		os.mkdir("./convertidos_PNG")
	except:
		pass

	try:
		os.mkdir("./processados")      
	except:
		pass


	# verificação e separação
	
	# path_inicial = input('insira o path da pasta com a sigla(ex: ADC):')

	# ler_arquivos_teste(path_inicial)


	# processamento dos textos separados

	path_2 = r'./processados'

	ler_arquivos(path_2)



#############################################################################


def Conversor_OCR(cmn_arq, pasta):

	print()
	print("-------------------------------")
	print("iniciando conversão das imagens")
	print("-------------------------------")
	print()

	# print(cmn_arq)
	# z = input('')
	# caminho do tesseract no computador
	pytesseract.tesseract_cmd ='C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

	# site pra baixar o tesseract
	# https://sourceforge.net/projects/tesseract-ocr-alt/files/tesseract-ocr-setup-3.02.02.exe/download


	# path para onde vão as imagens convertidas de PDF para PNG
	trl = r'./convertidos_PNG'

	try:
		os.mkdir(trl+"/"+pasta)
	except:
		pass
          
	# lê o arquivo e salva todas as imagens em uma lista


	img = convert_from_path(cmn_arq, dpi=200)
	# img[-1].save(trl+str(f)+'.png', 'PNG') # salvava só a última página


	nm_arq = str(cmn_arq).split("\\")[-1]
	nm_arq = str(nm_arq).split(".")[0]

	try:
		os.mkdir(trl+"/"+pasta+"/"+nm_arq)
	except:
		pass
	

	# path com as imagens convertidas em PNG
	path = r'./convertidos_PNG/'+pasta+"/"+str(nm_arq)



	# print(files)

	# Path para onde vão os TXT
	path_2 = r'./processados'
	try:
		os.mkdir(path_2+"/"+pasta)
	except:
		pass


	textos = []
	# coverte e salva todas as páginas na pasta
	for j in range(len(img)):
		print('estamos na página', j, 'de um total de', len(img))
		img[j].save(trl+"/"+pasta+"/"+str(nm_arq)+"/"+str(j)+'.png', 'PNG')
		time.sleep(1)
		text = pytesseract.image_to_string(trl+"/"+pasta+"/"+str(nm_arq)+"/"+str(j)+'.png', lang = 'por') # aciona o tesseract e coloca a linguagem em português
		textos.append(text)
		# print(text)
		# print()
             
	texto_final = " ".join(textos)     
	x = open(path_2+"/"+pasta+'/{}.txt'.format(str(nm_arq)), "w+")
	x.write(texto_final)
	x.close()
	print()
	print("                **************            ")



#########################################################################################################


def ler_arquivos_teste(diret):


	pastas = os.listdir(diret)

	q = 0
	for h in range(len(pastas)):
		q = q+1
		print("Estamos na pasta", pastas[h],"número",q)
		print('-------------------------------')
		cmn_pst = os.path.join(diret,pastas[h])
		arqs = os.listdir(cmn_pst)
		for arq in arqs:
			cmn_arq = os.path.join(cmn_pst,arq)
			# print(cmn_arq)
			texto = []
			with fitz.open(cmn_arq) as arquivo:
				for k in range(1):
					text = arquivo[k].get_text()
					texto.append(text)
				texto  = ' '.join(texto)

				if len(texto) < 10:
					Conversor_OCR(cmn_arq, pastas[h])
				else:
					try:
						os.mkdir("./processados/"+pastas[h])
					except:
						pass
					dst = r'./processados/'+pastas[h]
					shutil.copy(cmn_arq,dst)


#########################################################################################################


def ler_arquivos(path_2):


	# rgx_subs = re.compile("(?i)procuração")

	pastas = os.listdir(path_2)

	df_final = pd.DataFrame()
	df_relatorio = pd.DataFrame()
	acoes_boas =[]
	arquivos_bons =[]
	oabs_final =[]
	acoes_ruins = []
	tipos_arqs = []

	q = 0
	for h in range(4):#len(pastas)):
		q = q+1
		print("Estamos na pasta", pastas[h],"número",q)
		print('-------------------------------')
		cmn_pst = os.path.join(path_2,pastas[h])
		arqs = os.listdir(cmn_pst)
		for arq in arqs:
			cmn_arq = os.path.join(cmn_pst,arq)
			print("no arq", arq)
   
			extensao = cmn_arq[-3:]


			# se a extensão é txt
		    # print(extensao)
			if extensao == 'txt':
				with open(cmn_arq, "rb") as arquivo:
					texto = arquivo.read()
					# texto = str(texto)
					# print(type(texto))
					codificacao = chardet.detect(texto).get('encoding')
					# print(codificacao)
					texto = texto.decode(encoding=str(codificacao), errors='ignore')
					
					### Filtro de tamanho ###
					
					if len(texto) < 10000:


						# if re.search(rgx_subs, texto):
						# 	print("É subs:",cmn_arq)
						# 	print("--------------")
						# 	z = input("")
						# classificar(r'C:\Users\saylo\Desktop\projeto_redes_3\anotacao_procuracoes',texto)
						x,df,nome = classificar_spacy(texto)
						if x == True:
							# docs_bons.append(arq)
							# df_final = pd.concat([df_final,df])
							# print(cmn_arq)
							# print("--------------")
							# z = input("")
							try:
								oab_list = [item for item in df["OAB"].to_list()]
								oab_list = " ".join(oab_list)
								oabs = sep_representante(oab_list)							
								for oab in oabs:
									oabs_final.append(oab)
									acoes_boas.append(pastas[h])
									arquivos_bons.append(arq)
									tipos_arqs.append(nome)
							except:
								# print("pegou pelo texto")
								oabs = sep_representante(texto)
								for oab in oabs:
									oabs_final.append(oab)
									acoes_boas.append(pastas[h])
									arquivos_bons.append(arq)
									tipos_arqs.append(nome)
						else:
							df_relatorio = pd.concat([df_relatorio,df],ignore_index= True)
					# else:
					# 	print("Eliminado pelo tamanho")
					#### avaliar a petição inicial aqui

					

			elif extensao == 'pdf':
				with fitz.open(cmn_arq) as arquivo:
					texto = []
					pg_1 = []
					for n in range(len(arquivo)):
						texto.append(arquivo[n].get_text().strip())
						if n == 0:
						   pg_1.append(arquivo[n].get_text().strip())

					texto = " ".join(texto)
					# if re.search(rgx_subs, texto):
					# 	print("É subs:",cmn_arq)
					# 	print("--------------")
					# 	z = input("")

					### Filtro de tamanho ###

					if len(texto) < 10000:

					
						# classificar(r'C:\Users\saylo\Desktop\projeto_redes_3\anotacao_procuracoes',texto)
						x,df,nome = classificar_spacy(texto)
						if x == True:
							# docs_bons.append(arq)
							# df_final = pd.concat([df_final,df],ignore_index= True)
							# print(cmn_arq)
							# print("--------------")
							# z = input("")
							try:
								oab_list = [item for item in df["OAB"].to_list()]
								oab_list = " ".join(oab_list)
								oabs = sep_representante(oab_list)
								for oab in oabs:
									oabs_final.append(oab)
									acoes_boas.append(pastas[h])
									arquivos_bons.append(arq)
									tipos_arqs.append(nome)
							
							except:
								# print("pegou pelo texto")
								oabs = sep_representante(texto)
								for oab in oabs:
									oabs_final.append(oab)
									acoes_boas.append(pastas[h])
									arquivos_bons.append(arq)
									tipos_arqs.append(nome)

						else:
							acoes_ruins.append(pastas[h])
							# df.insert(loc = 0, column = "documento", value = arq)
							# df_relatorio = pd.concat([df_relatorio,df], ignore_index= True)
							# pass
					# else:
					# 	print("Eliminado pelo tamanho")
						#### avaliar a petição inicial aqui


	
	df_final["Nome_Acao"] = acoes_boas
	df_final["OAB"] = oabs_final
	df_final["Arquivo"] = arquivos_bons
	df_final["Tipo_documento"] = tipos_arqs			
	df_final.to_excel('banco_dados_redes_oabs.xlsx', index = False)

	acoes_ruins =[ acao for acao in acoes_ruins if acao not in acoes_boas]

	df_relatorio["Ações sem procuração ou inicial"] = acoes_ruins

	df_relatorio.drop_duplicates(subset = ["Ações sem procuração ou inicial"], inplace = True)

	# df_relatorio.insert(loc = 0, column = "documento", value = docs_ruins, allow_duplicates=True)
	df_relatorio.to_excel('relatorio_redes_nao_encontrados.xlsx', index = False)


#########################################################################################################

if __name__ == "__main__":
	Main()