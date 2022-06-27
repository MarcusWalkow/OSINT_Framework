import sys 
from itertools import product
def possible_emails(args):
    providers = ["@web.de","@gmx.de","@gmail.com","@t-online","@outlook.com","@yahoo.com"]
    possibile_names = []
    names= args.split(" ")
    vor, nach = [name[:1] for name in names]
    possibile_names.append(f"{vor}.{names[1]}")
    possibile_names.append(f"{names[0]}.{nach}")
    possibile_names.append(args.replace(" ","."))
    possibile_names.append(args.replace(" ","_"))
    return [*map(''.join, product (possibile_names,providers))]

if __name__ == '__main__':
    input=str(sys.argv[1])  
    print(possible_emails(input))



