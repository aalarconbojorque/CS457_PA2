USE CS457_PA2;

select * from Product;

update Product 
set name = 'Gizmo' 
where name = 'SuperGizmo';

update Product 
set price = 14.99 
where name = 'Gizmo';

.exit