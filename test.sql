--CS457 PA2 test script


USE CS457_PA2;


select * from Product;

select * from product where name != 'Gizmo';

select name, pid from product where name = 'Gizmo';

select name, price from product where name = 'SuperGizmo';

select price, name from product where name = 'SuperGizmo';




.exit