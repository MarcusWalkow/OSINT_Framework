#https://huggingface.co/fhswf/bert_de_ner?text=Moskau+liefert+Polen+und+Bulgarien+kein+Gas+mehr
#vohrer tensorflow, transformers und torch mit pip installieren
from base64 import encode
from transformers import pipeline
import sys
import csv

def german_ner(text):
    combined_ner_token=[]
    final_list=[]
    indizes =[]
    ner=[]

    classifier = pipeline('ner', model="fhswf/bert_de_ner")
    ner_transformation_result = classifier(text)
    ner_token = [elem['word'] for elem in ner_transformation_result]

    #zusammenhängende NER Token in einer seperaten Liste speichern
    #gleichzeitig diese Token aus der ner_token Liste löschen
    for index in reversed(indizes):
        combined_ner_token.append([ner_token[index-1],ner_token[index]])
        ner_token.remove(ner_token[index])
        ner_token.remove(ner_token[index-1])


    ner.extend(combined_ner_token)
    ner.extend(ner_token)

    #Wörter aus dem Text als Liste speichern
    for list_elem in text.split():
        #jedes NER Token
        for ner_elem in ner:
            #Prüfen, ob es sich um eine Liste zusammengehöriger NER Token handelt
            if type(ner_elem)== list:
                #es wird das Wort gesucht, in dem alle zusammengehörigen NER Token vorkommen
                for sub_ner_elem in ner_elem:
                    first_found=""
                    #dafür sorgen, das beide Teilwörter aus der ner_token auch im selben Wort vorkommen.
                    if sub_ner_elem.casefold() in list_elem.casefold(): #casefold lässt ein ignoriert Groß und Kleinschreibung beim Vergleichen 
                        if list_elem == first_found:
                            final_list.append(list_elem)
                        #das gefundene Wort zum ersten Token der zusammengehörigen NER Token wird gespeichert, damit darüber geprüft werden kann, ob die anderen NER Token auch reinpassen  
                        first_found=list_elem
            #handelt es sich um ein einzelnes NER Token, wird das mit allen Wörtern aus dem Satz vergliuchen
            if ner_elem.casefold() in list_elem.casefold(): #casefold ist für case insensitives Vergleichen
                final_list.append(list_elem)
    #Dopplungen entfernen
    final_list =list(set(final_list))
    return(final_list)


if __name__ == '__main__':  
    
    text_file_path = sys.argv[1]
    #delimiter = sys.argv[2]
    result=[]
   # print(delimiter)
    #print(f"text_file_path {text_file_path}")
    
    with open(text_file_path,encoding="latin-1") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = "\n" )
        for row in csv_reader:
            #print(row)
            result.extend(german_ner(str(row)))

    print(result)