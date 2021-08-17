## TEKNOLANDIN

İnternet üzeri ürün alım/satımı için geliştirilen web uygulaması. 
Uygulamada Admin ürün eklemesi yapıp bunları kullanıcılara sunabilir. Kullanıcılar ise bütçesi yettiği sürece ürünleri stokta bulundukça alabilmektedir. Ayrıca ürün iadesi ve kampanyalar gibi özellikler de bulunmaktadır.

Projenin daha detaylı anlatımı için lütfen raporu okuyunuz.

## Team:
Bahadır Altun<br/>
Talha Doğukan Gaffaroğlu<br/>
Mert İkinci<br/>

## Setup:
You should have a postgresql setup. Please refer [here](https://www.postgresql.org/download/) for installation.
<br />
**Packages that is needed to run:**   
   > pip install flask flask-sqlalchemy  <br/>
   > pip install psychopg2 <br/>
   > pip install pymongo <br/>
   > pip install Flask-PyMongo <br/>
   
   
 **to run:**    
   > python app.py 
   
    
 You can add the database tables by running dump.sql and if your settings  are different you need to change the 'postgresql://postgres:tdg123@localhost/teknolandin' part by using this format: 
 
 >postgresql://\<username\>:\<password\>@localhost/\<databasename\>  
 
