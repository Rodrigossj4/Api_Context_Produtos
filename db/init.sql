\c ecommerce;

Create Table secao(
	id serial primary key,
	Nome varchar(100) not null,
	Ativa bool default true
);

insert into secao("nome") values('secao 1');
insert into secao("nome") values('secao 2');

Create Table produtos(
	id serial primary key,
	Nome varchar(250) not null,
	Preco numeric not null,
	idSecao int not null,
	Ativa bool default true,
	foreign key (idSecao) references secao(id)
);