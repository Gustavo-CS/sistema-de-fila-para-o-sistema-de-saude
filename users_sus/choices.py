from django.db import models

class Estados(models.TextChoices):
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espírito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'

UNIDADES_POR_ESTADO = {
    'AC': [
        ('HCAC', 'Hospital das Clínicas do Acre (HCAC)'),
        ('HUEAC', 'Hospital de Urgência e Emergência de Rio Branco (HUEAC)'),
        ('UBSManoelJulao', 'UBS Manoel Julião'),
    ],
    'AL': [
        ('HGE', 'Hospital Geral do Estado (HGE) - Maceió'),
        ('HospitalMulherAL', 'Hospital da Mulher - Maceió'),
        ('UPAEustaquio', 'UPA Eustáquio Gomes - Maceió'),
    ],
    'AP': [
        ('HEMAC', 'Hospital de Emergência de Macapá (HEMAC)'),
        ('HospitalMulherAP', 'Hospital da Mulher de Macapá'),
        ('UBSCentralAP', 'UBS Central de Macapá'),
    ],
    'AM': [
        ('HPS28Agosto', 'Hospital e Pronto-Socorro 28 de Agosto – Manaus'),
        ('HospitalJoaoLucio', 'Hospital João Lúcio – Manaus'),
        ('UBSSaoFranciscoAM', 'UBS São Francisco – Manaus'),
    ],
    'BA': [
        ('HGEBA', 'Hospital Geral do Estado (HGE) – Salvador'),
        ('HospitalRobertoSantos', 'Hospital Roberto Santos – Salvador'),
        ('UPACajazeiras', 'UPA Cajazeiras – Salvador'),
    ],
    'CE': [
        ('HGCE', 'Hospital Geral de Fortaleza'),
        ('HospitalAlbertSabin', 'Hospital Infantil Albert Sabin'),
        ('UPAIracema', 'UPA Iracema'),
    ],
    'DF': [
        ('HBDF', 'Hospital de Base do Distrito Federal (HBDF)'),
        ('HRAN', 'Hospital Regional da Asa Norte (HRAN)'),
        ('UPACeilandia', 'UPA Ceilândia'),
    ],
    'ES': [
        ('HGEES', 'Hospital Estadual de Urgência e Emergência de Vitória'),
        ('HospitalCriançaES', 'Hospital Infantil de Vitória'),
        ('UPAJardimCamburi', 'UPA Jardim Camburi'),
    ],
    'GO': [
        ('HGGoiânia', 'Hospital Geral de Goiânia'),
        ('HospitalAnisioTeixeira', 'Hospital Anísio Teixeira'),
        ('UPAPiedade', 'UPA Piedade'),
    ],
    'MA': [
        ('HGMaranhão', 'Hospital Geral de Maranhão'),
        ('HospitalMaternoInfantilMA', 'Hospital Materno Infantil de São Luís'),
        ('UPAAnil', 'UPA Anil'),
    ],
    'MT': [
        ('HGMT', 'Hospital Geral de Mato Grosso'),
        ('HospitalSantaCruzMT', 'Hospital Santa Cruz - Cuiabá'),
        ('UPACuiabá', 'UPA Cuiabá'),
    ],
    'MS': [
        ('HGUFMS', 'Hospital Geral Universitário de Mato Grosso do Sul'),
        ('HospitalCoraçãoMS', 'Hospital do Coração de Campo Grande'),
        ('UPACampoGrande', 'UPA Campo Grande'),
    ],
    'MG': [
        ('HUMG', 'Hospital das Clínicas da UFMG'),
        ('HospitalOdilonBehrens', 'Hospital Odilon Behrens'),
        ('UPAPampulha', 'UPA Pampulha'),
    ],
    'PA': [
        ('HGPAA', 'Hospital Geral de Belém'),
        ('HospitalBarrosBarreto', 'Hospital Barros Barreto'),
        ('UPABelém', 'UPA Belém'),
    ],
    'PB': [
        ('HGPB', 'Hospital de Trauma de João Pessoa'),
        ('HospitalCruzVermelhaPB', 'Hospital Cruz Vermelha - João Pessoa'),
        ('UPAJoãoPessoa', 'UPA João Pessoa'),
    ],
    'PR': [
        ('HCParaná', 'Hospital de Clínicas da UFPR'),
        ('HospitalEvangelico', 'Hospital Evangélico de Curitiba'),
        ('UPACuritiba', 'UPA Curitiba'),
    ],
    'PE': [
        ('HGPernambuco', 'Hospital das Clínicas da UFPE'),
        ('HospitalOswaldoCruz', 'Hospital Oswaldo Cruz - Recife'),
        ('UPARecife', 'UPA Recife'),
    ],
    'PI': [
        ('HGPi', 'Hospital Getúlio Vargas'),
        ('HospitalRegionalPI', 'Hospital Regional de Teresina'),
        ('UPATeresina', 'UPA Teresina'),
    ],
    'RJ': [
        ('HCOR', 'Hospital das Clínicas de Corrêas'),
        ('HospitalGomesFaria', 'Hospital Municipal Carlos G. Faria'),
        ('UPARio', 'UPA Rio de Janeiro'),
    ],
    'RN': [
        ('HGRN', 'Hospital Giselda Trigueiro'),
        ('HospitalSantaCatarinaRN', 'Hospital Santa Catarina - Natal'),
        ('UPANatal', 'UPA Natal'),
    ],
    'RS': [
        ('HCPortoAlegre', 'Hospital de Clínicas de Porto Alegre'),
        ('HospitalSãoLucas', 'Hospital São Lucas - Porto Alegre'),
        ('UPAPortoAlegre', 'UPA Porto Alegre'),
    ],
    'RO': [
        ('HGRO', 'Hospital Regional de Ji-Paraná'),
        ('HospitalCacoal', 'Hospital Municipal de Cacoal'),
        ('UPAJiParaná', 'UPA Ji-Paraná'),
    ],
    'RR': [
        ('HGNRR', 'Hospital Geral de Roraima'),
        ('HospitalMaternoInfantilRR', 'Hospital Materno Infantil de Roraima'),
        ('UPARR', 'UPA Boa Vista'),
    ],
    'SC': [
        ('HCSC', 'Hospital de Clínicas de Santa Catarina'),
        ('HospitalRegionalSC', 'Hospital Regional de Joinville'),
        ('UPAScJoinville', 'UPA Joinville'),
    ],
    'SP': [
        ('HCUSP', 'Hospital das Clínicas da FMUSP – São Paulo'),
        ('HGSP', 'Hospital Geral de São Paulo (HGSP)'),
        ('UPAVilaFormosa', 'UPA Vila Formosa – São Paulo'),
    ],
    'SE': [
        ('HGSE', 'Hospital de Urgência de Sergipe'),
        ('HospitalCirurgiaSergipe', 'Hospital de Cirurgia - Aracaju'),
        ('UPAAracaju', 'UPA Aracaju'),
    ],
    'TO': [
        ('HGTO', 'Hospital Geral de Palmas'),
        ('HospitalRegionalTO', 'Hospital Regional de Gurupi'),
        ('UPAPalmas', 'UPA Palmas'),
    ],
}