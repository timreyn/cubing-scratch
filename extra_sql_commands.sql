alter table Results add column id int(10) unsigned primary key AUTO_INCREMENT;
alter table Competitions add primary key(id);
alter table Events add primary key(id);
alter table Countries add primary key(id);
-- Create indices.
create index competitionId on Results (competitionId);
create index eventId on Results (eventId);
create index roundTypeId on Results (roundTypeId);
create index personId on Results (personId);
create index personCountryId on Results (personCountryId);

create index id ON Competitions (id);
create index countryId ON Competitions (countryId);

create index id ON Persons (id);

create index id ON Countries (id);

alter table Competitions add column startDate date;
alter table Competitions add column endDate date;
update Competitions set startDate = year * 10000 + month * 100 + day;
update Competitions set endDate = (CASE WHEN endMonth < month THEN year + 1 ELSE year END) * 10000 + endMonth * 100 + endDay;
alter table Competitions add column state varchar(50);
update Competitions set state = substring(cityName, position("," in cityName) + 2, 900) where countryId in ("USA", "Australia", "Canada", "India", "Brazil", "United Kingdom") and cityName not like "%Multiple cities%" and cityName not like "%Múltiplas cidades%";
update Competitions set state = "Paraná" where state="PR" and countryId="Brazil";
create index state on Competitions (state);

drop table if exists UniquePersons;
create table UniquePersons
select id, name, countryId, gender from Persons where subId = 1;
alter table UniquePersons add primary key(id);

drop table if exists state_counts;
create table state_counts
select
  UniquePersons.id as personId,
  UniquePersons.name as name,
  Competitions.countryId as countryId,
  count(distinct state) as num
from
  Results
  join UniquePersons on Results.personId = UniquePersons.id
  join Competitions on Results.competitionId = Competitions.id
where
  state is not null
group by
  personId, countryId, name;

drop table if exists in_state_records_single;
create table in_state_records_single
select
  t.state as state,
  t.eventId as eventId, 
  personId as personId,
  competitionId as competitionId,
  countryId as countryId,
  t.result as result
from
  Results
  join Competitions on Results.competitionId = Competitions.id
  join (
    select state, eventId, min(best) as result
    from Results join Competitions on Results.competitionId = Competitions.id
    where state is not null and best > 0
    group by state, eventId) t
  on Competitions.state = t.state and Results.eventId = t.eventId and Results.best = t.result;
create index state on in_state_records_single (state);
create index countryId on in_state_records_single (countryId);
create index eventId on in_state_records_single (eventId);
create index personId on in_state_records_single (personId);

drop table if exists in_state_records_average;
create table in_state_records_average
select
  t.state as state,
  t.eventId as eventId, 
  personId as personId,
  competitionId as competitionId,
  countryId as countryId,
  t.result as result
from
  Results
  join Competitions on Results.competitionId = Competitions.id
  join (
    select state, eventId, min(average) as result
    from Results join Competitions on Results.competitionId = Competitions.id
    where state is not null and average > 0
    group by state, eventId) t
  on Competitions.state = t.state and Results.eventId = t.eventId and Results.average = t.result;
create index state on in_state_records_average (state);
create index countryId on in_state_records_average (countryId);
create index eventId on in_state_records_average (eventId);
create index personId on in_state_records_average (personId);


drop table if exists states;
create table states (state_name varchar(50), country_id varchar(50), region_id varchar(5), state_id varchar(5));
insert into states (state_name, country_id, region_id, state_id) values
("Alabama", "USA", "SE", "AL"),
("Alaska", "USA", "NW", "AK"),
("Arizona", "USA", "W", "AZ"),
("Arkansas", "USA", "S", "AR"),
("California", "USA", "W", "CA"),
("Colorado", "USA", "W", "CO"),
("Connecticut", "USA", "NE", "CT"),
("Delaware", "USA", "NE", "DE"),
("Florida", "USA", "SE", "FL"),
("Georgia", "USA", "SE", "GA"),
("Hawaii", "USA", "W", "HI"),
("Idaho", "USA", "NW", "ID"),
("Illinois", "USA", "GL", "IL"),
("Indiana", "USA", "GL", "IN"),
("Iowa", "USA", "HL", "IA"),
("Kansas", "USA", "HL", "KS"),
("Kentucky", "USA", "GL", "KY"),
("Louisiana", "USA", "S", "LA"),
("Maine", "USA", "NE", "ME"),
("Maryland", "USA", "NE", "MD"),
("Massachusetts", "USA", "NE", "MA"),
("Michigan", "USA", "GL", "MI"),
("Minnesota", "USA", "HL", "MN"),
("Mississippi", "USA", "S", "MS"),
("Missouri", "USA", "HL", "MO"),
("Montana", "USA", "NW", "MT"),
("Nebraska", "USA", "HL", "NE"),
("Nevada", "USA", "W", "NV"),
("New Hampshire", "USA", "NE", "NH"),
("New Jersey", "USA", "NE", "NJ"),
("New Mexico", "USA", "S", "NM"),
("New York", "USA", "NE", "NY"),
("North Carolina", "USA", "SE", "NC"),
("North Dakota", "USA", "HL", "ND"),
("Ohio", "USA", "GL", "OH"),
("Oklahoma", "USA", "S", "OK"),
("Oregon", "USA", "NW", "OR"),
("Pennsylvania", "USA", "NE", "PA"),
("Rhode Island", "USA", "NE", "RI"),
("South Carolina", "USA", "SE", "SC"),
("South Dakota", "USA", "HL", "SD"),
("Tennessee", "USA", "SE", "TN"),
("Texas", "USA", "S", "TX"),
("Utah", "USA", "W", "UT"),
("Vermont", "USA", "NE", "VT"),
("Virginia", "USA", "NE", "VA"),
("Washington", "USA", "NW", "WA"),
("West Virginia", "USA", "NE", "WV"),
("Wisconsin", "USA", "GL", "WI"),
("Wyoming", "USA", "NW", "WY"),
("New South Wales", "Australia", "AU", "NSW"),
("Queensland", "Australia", "AU", "QLD"),
("South Australia", "Australia", "AU", "SA"),
("Tasmania", "Australia", "AU", "TAS"),
("Victoria", "Australia", "AU", "VIC"),
("Western Australia", "Australia", "AU", "WA"),
("Australian Capital Territory", "Australia", "AU", "ACT"),
("Northern Territory", "Australia", "AU", "NT"),
("Alberta", "Canada", "CA", "AB"),
("British Columbia", "Canada", "CA", "BC"),
("Ontario", "Canada", "CA", "ON"),
("Manitoba", "Canada", "CA", "MB"),
("New Brunswick", "Canada", "CA", "NB"),
("Newfoundland and Labrador", "Canada", "CA", "NL"),
("Northwest Territories", "Canada", "CA", "NT"),
("Nova Scotia", "Canada", "CA", "NS"),
("Nunavut", "Canada", "CA", "NU"),
("Prince Edward Island", "Canada", "CA", "PE"),
("Quebec", "Canada", "CA", "QC"),
("Saskatchewan", "Canada", "CA", "SK"),
("Yukon", "Canada", "CA", "YT"),
("Bedfordshire","United Kingdom","EOE","BED"),
("Berkshire","United Kingdom","SEE","BER"),
("City of Bristol","United Kingdom","SWE","BRI"),
("Buckinghamshire","United Kingdom","SEE","BUC"),
("Cambridgeshire","United Kingdom","EOE","CAM"),
("Cheshire","United Kingdom","NWE","CHE"),
("City of London","United Kingdom","GLN","LON"),
("Cornwall","United Kingdom","SWE","COR"),
("Cumbria","United Kingdom","NWE","CUM"),
("Derbyshire","United Kingdom","EMD","DER"),
("Devon","United Kingdom","SWE","DEV"),
("Dorset","United Kingdom","SWE","DOR"),
("Durham","United Kingdom","NEE","DUR"),
("East Riding of Yorkshire","United Kingdom","YRH","ERY"),
("East Sussex","United Kingdom","SEE","ESU"),
("Essex","United Kingdom","EOE","ESS"),
("Gloucestershire","United Kingdom","SWE","GLO"),
("Greater London","United Kingdom","GLN","GLN"),
("Greater Manchester","United Kingdom","NWE","GRM"),
("Hampshire","United Kingdom","SEE","HAM"),
("Herefordshire","United Kingdom","WMD","HER"),
("Hertfordshire","United Kingdom","EOE","HRT"),
("Isle of Wight","United Kingdom","SEE","IOW"),
("Kent","United Kingdom","SEE","KNT"),
("Lancashire","United Kingdom","NWE","LAN"),
("Leicestershire","United Kingdom","EMD","LEI"),
("Lincolnshire","United Kingdom","EMD","LIN"),
("Merseyside","United Kingdom","NWE","MER"),
("Norfolk","United Kingdom","EOE","NFK"),
("North Yorkshire","United Kingdom","YRH","NYK"),
("Northamptonshire","United Kingdom","EMD","NHP"),
("Northumberland","United Kingdom","NEE","NHU"),
("Nottinghamshire","United Kingdom","EMD","NOT"),
("Oxfordshire","United Kingdom","SEE","OXF"),
("Rutland","United Kingdom","EMD","RUT"),
("Shropshire","United Kingdom","WMD","SHR"),
("Somerset","United Kingdom","SWE","SOM"),
("South Yorkshire","United Kingdom","YRH","SYK"),
("Staffordshire","United Kingdom","WMD","STA"),
("Suffolk","United Kingdom","EOE","SUF"),
("Surrey","United Kingdom","SEE","SUR"),
("Tyne and Wear","United Kingdom","NEE","TYW"),
("Warwickshire","United Kingdom","WMD","WAR"),
("West Midlands","United Kingdom","WMD","WMI"),
("West Sussex","United Kingdom","SEE","WSU"),
("West Yorkshire","United Kingdom","YRH","WYO"),
("Wiltshire","United Kingdom","SWE","WLT"),
("Worcestershire","United Kingdom","WMD","WOR"),
("City of Edinburgh","United Kingdom","SCT","EDN"),
("Gwent","United Kingdom","WLS","GWE"),
("County Antrim","United Kingdom","NIR","ANT"),
("Acre","Brazil","BRN","AC"),
("Alagoas","Brazil","BRNE","AL"),
("Amapá","Brazil","BRN","AP"),
("Amazonas","Brazil","BRN","AM"),
("Bahia","Brazil","BRNE","BA"),
("Ceará","Brazil","BRNE","CE"),
("Distrito Federal","Brazil","BRCW","DF"),
("Espírito Santo","Brazil","BRSE","ES"),
("Goiás","Brazil","BRCW","GO"),
("Maranhão","Brazil","BRNE","MA"),
("Mato Grosso","Brazil","BRCW","MT"),
("Mato Grosso do Sul","Brazil","BRCW","MS"),
("Minas Gerais","Brazil","BRSE","MG"),
("Pará","Brazil","BRN","PA"),
("Paraíba","Brazil","BRNE","PB"),
("Paraná","Brazil","BRS","PR"),
("Pernambuco","Brazil","BRNE","PE"),
("Piauí","Brazil","BRNE","PI"),
("Rio de Janeiro","Brazil","BRSE","RJ"),
("Rio Grande do Norte","Brazil","BRNE","RN"),
("Rio Grande do Sul","Brazil","BRS","RS"),
("Rondônia","Brazil","BRN","RO"),
("Roraima","Brazil","BRN","RR"),
("Santa Catarina","Brazil","BRS","SC"),
("São Paulo","Brazil","BRSE","SP"),
("Sergipe","Brazil","BRNE","SE"),
("Tocantins","Brazil","BRN","TO"),
("Andhra Pradesh","India","INS","AP"),
("Arunachal Pradesh","India","INNE","AR"),
("Assam","India","INNE","AS"),
("Bihar","India","INE","BR"),
("Chhattisgarh","India","INC","CT"),
("Goa","India","INW","GA"),
("Gujarat","India","INW","GJ"),
("Haryana","India","INN","HR"),
("Himachal Pradesh","India","INN","HP"),
("Jharkhand","India","INE","JH"),
("Karnataka","India","INS","KA"),
("Kerala","India","INS","KL"),
("Madhya Pradesh","India","INC","MP"),
("Maharashtra","India","INW","MH"),
("Manipur","India","INNE","MN"),
("Meghalaya","India","INNE","ML"),
("Mizoram","India","INNE","MZ"),
("Nagaland","India","INNE","NL"),
("Odisha","India","INE","OD"),
("Punjab","India","INN","PB"),
("Rajasthan","India","INN","RJ"),
("Sikkim","India","INNE","SK"),
("Tamil Nadu","India","INS","TN"),
("Telangana","India","INS","TG"),
("Tripura","India","INNE","TR"),
("Uttar Pradesh","India","INN","UP"),
("Uttarakhand","India","INN","UT"),
("West Bengal","India","INE","WB"),
("Andaman and Nicobar Islands","India","INS","AN"),
("Chandigarh","India","INN","CH"),
("Dadra and Nagar Haveli and Daman and Diu","India","INW","DD"),
("Jammu and Kashmir","India","INN","JK"),
("Ladakh","India","INN","LA"),
("Lakshadweep","India","INS","LD"),
("Delhi","India","INN","DL"),
("Puducherry","India","INS","PY");

drop table if exists regions;
create table regions (country_id varchar(50), region_id varchar(5), region_name varchar(50));
insert into regions (country_id, region_id, region_name) values
("USA", "HL", "Heartlands"),
("USA", "GL", "Great Lakes"),
("USA", "SE", "Southeast"),
("USA", "NE", "Northeast"),
("USA", "W", "West"),
("USA", "NW", "Northwest"),
("USA", "S", "South"),
("Australia", "AU", "Australia"),
("Canada", "CA", "Canada"),
("United Kingdom", "NWE", "North West England"),
("United Kingdom", "NEE", "North East England"),
("United Kingdom", "SWE", "South West England"),
("United Kingdom", "SEE", "South East England"),
("United Kingdom", "EOE", "East of England"),
("United Kingdom", "GLN", "Greater London"),
("United Kingdom", "WMD", "West Midlands"),
("United Kingdom", "EMD", "East Midlands"),
("United Kingdom", "YRH", "Yorkshire and the Humber"),
("United Kingdom", "SCT", "Scotland"),
("United Kingdom", "NIR", "Northern Ireland"),
("United Kingdom", "WLS", "Wales"),
("Brazil","BRN","North Region"),
("Brazil","BRNE","Northeast Region"),
("Brazil","BRCW","Central-West Region"),
("Brazil","BRSE","Southeast Region"),
("Brazil","BRS","South Region"),
("India","INS","South India"),
("India","INNE","Northeast India"),
("India","INE","East India"),
("India","INC","Central India"),
("India","INW","Western India"),
("India","INN","North India");
