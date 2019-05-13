import PyPDF2
import re
import sys
import pymysql
import mysql.connector
import os

db = pymysql.connect(db="pengemasan", user="root", passwd="", host="127.0.0.1", port=3306)
cursor = db.cursor()

cursor.execute("TRUNCATE TABLE tb_register_spt")
db.commit()

def cariNomorRegister(teks):
	noregs  = re.findall(r'REG\-\d+\/\w+\/\w+\.\d+\/\w+\.\d+\/\d{4}',teks)
	noreg  = noregs[0]
	noreg  = str(noreg)
	
	return noreg
	
def cariTanggalRegister(teks):
	tgl_register = teks.split("SPT")
	tgl_register = tgl_register[0]
	tgl_register = tgl_register.split(" : ")
	tgl_register = tgl_register[1]
	tgl_register = tgl_register.strip()	
	
	return tgl_register

berkasRegister = []
jumlahBerkasRegister = 0
jumlahBPS = 0

for filename in os.listdir('.'):
	if filename.endswith('.pdf') and filename.startswith('REG-'):
		berkasRegister.append(filename)
		
berkasRegister.sort(key=str.lower)

for berkas in berkasRegister:
	bukaBerkas = open(berkas,'rb')
	bacaBerkas = PyPDF2.PdfFileReader(bukaBerkas)
	bacaHalamanSatu = bacaBerkas.getPage(0)
	hasilBacaHalamanSatu = bacaHalamanSatu.extractText()
	
	NomorRegister = cariNomorRegister(hasilBacaHalamanSatu)
	TanggalRegister = cariTanggalRegister(hasilBacaHalamanSatu)
	
	print("===============================================================================================================")
	print("No Register : " + NomorRegister + " Tanggal Register : " + TanggalRegister)
	print("===============================================================================================================")
	print("\n")	
	
	jumlahHalaman = bacaBerkas.getNumPages()
	jumlahBerkasRegister += 1
		
	for halaman in range(jumlahHalaman):
		bacaHalaman = bacaBerkas.getPage(halaman)
		hasilBaca = bacaHalaman.extractText()
		
		print("Halaman ",str(halaman + 1))
		
		npwps = re.findall(r'\d{2}\.\d{3}\.\d{3}\.\d{1}\-\d{3}\.\d{3}',hasilBaca)
		bpss  = re.findall(r'S\-\d+\/\w+\/\w+\.\d+\/\w+\.\d+\/\d{4}',hasilBaca)
	
		kamus = dict(zip(bpss, npwps))
		
		for x,y in kamus.items():
			barisPertama = "Nomor Register : " + str(NomorRegister) + " Tgl Register : " + str(TanggalRegister) + " No BPS : " + str(x) + " NPWP : " +  str(y)
			print("------------------------------------------------------------------------------------")
			print(barisPertama)
			print("------------------------------------------------------------------------------------")
			cursor.execute("INSERT INTO tb_register_spt (no_reg,tgl_str_reg,no_bps,npwp) VALUES ('" + NomorRegister + "','" + TanggalRegister+ "','" + x + "','" + y + "')")
			db.commit()
			jumlahBPS += 1
			print("Jumlah BPS : " + str(jumlahBPS))
			print("------------------------------------------------------------------------------------")
print("\n")		
print("Jumlah Berkas Register : ",jumlahBerkasRegister,"Register")

cursor.execute("UPDATE tb_register_spt SET tgl_reg = SUBSTRING_INDEX(tgl_str_reg,' ',1)")
db.commit()

cursor.execute("UPDATE tb_register_spt SET bln_reg = SUBSTRING_INDEX(SUBSTRING_INDEX(tgl_str_reg,' ',2),' ',-1)")
db.commit()

cursor.execute("UPDATE tb_register_spt SET thn_reg = SUBSTR(tgl_str_reg,-4)")
db.commit()

cursor.execute("UPDATE tb_register_spt SET kd_jns_spt = SUBSTRING_INDEX(SUBSTRING_INDEX(no_bps,'/',-4),'/',1)")
db.commit()

db.close()

print("\n")
print("================== THE JOB IS DONE ! =======================\n")