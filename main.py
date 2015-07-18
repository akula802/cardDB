#! usr/bin/env Python3

###########################################################################################################
###########################################################################################################
###                                                                                                     ###
###                                          CardDB version 1.4                                         ###
###                                            April 17, 2015                                           ###
###                                                                                                     ###
###              A simple, yet powerful database application to store baseball card records.            ###
###          Written in Python 3.4, with the psycopg v2.6 library for PostgreSQL v9.4 connection.       ###
###                                                                                                     ###
###                                     Copyright 2015 Brian Hartley                                    ###
###                                         All rights reserved.                                        ###
###                                                                                                     ###
###                                www.bhartley.com  |  brian@bhartley.com                              ###
###                                                                                                     ###
###########################################################################################################
###########################################################################################################


import datetime
import os
import psycopg2
import re
import texttable as tt


#---OPEN_START--------------------------------------------------------------------------------------------------


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Try to establish database connection first, print a message and quit if unable
try:
    conn = psycopg2.connect("dbname='cards' user='py_carddb' host='localhost' port='5432' password='password'")
    clear_screen()
    print('\n     <<< Database connection established! >>>\n')
    print('             Welcome to CardDB v1.4')
    print('_' * 50)
except:
    clear_screen()
    print('\n<<< Unable to establish database connection. >>>\n')
    quit()


# Global variables
cur = conn.cursor()
message = ''
add_data = {}

columns_actual = {'i': 'ID', 's': 'sport', 'l': 'lastName', 'f': 'firstName', 'y': 'year', 't': 'team', 
            'c': 'company', 'v': 'valueEst', 'd': 'saleDate', 'p': 'salePrice'}

columns_disp = {'i': 'ID', 's': 'sport', 'l': 'last name', 'f': 'first name', 'y': 'year', 't': 'team', 
            'c': 'company', 'v': 'estimated value', 'd': 'sale date', 'p': 'sale price'}


def main_menu():
    # Displays the main menu with top-level options for database interaction
    global message
    global add_data
    
    add_data = {}
    
    if len(message) > 0:
        print(message)
        message = ''

    print('\n MAIN MENU: select desired operation.\n')
        
    menu_choice = input(' [A]dd, [S]earch, [E]dit, [V]end, [D]elete, or [Q]uit >> ').strip().lower()
    
    # Validate main menu inputs
    if menu_choice == 'a':
        add_card()
    elif menu_choice == 's':
        search()
    elif menu_choice == 'e':
        edit_card()
    elif menu_choice == 'v':
        vend_card()
    elif menu_choice == 'd':
        delete_card()
    elif menu_choice == 'q':
        quit_carddb()
    else:
        clear_screen()
        print('\n     <<< Invalid selection >>>')
        print('_' * 50)
        main_menu()


#---UTILITIES--------------------------------------------------------------------------------------------------


def validate_varchar(inp):
    # Form validation for varchar columns
    try:
        xx = str(inp)
        if len(xx) in range(1, 50):
            return True
        else:
            return False
    except:
        return False


def remove_special(inp):
    try:
        xx = re.sub('[;\':><?$%*"+=|{}\[\]#@!,_\\\/&^().~]', '', inp)
        return xx
    except:
        return False


def validate_year(inp):
    # Form validation for year columns
    try:
        xx = int(inp)
        if len(str(xx)) == 4:
            if xx in range(1900, 2025):
                return True
        else:
            return False
    except:
        return False


def validate_date(inp):
    # Form validation for date columns
    if inp == 'Q' or inp == 'q':
        return 'Q'
        
    fmt = '%Y-%m-%d'
    try:
        datetime.datetime.strptime(inp, fmt)
        return True
    except:
        return False


def validate_price(inp):
    # Form validation for price columns
    if inp == 'Q' or inp == 'q':
        return 'Q'
    try:
        xx = float(inp)
        if xx >= 0.00 and xx <= 99999.99:
            return True
        else:
            return False
    except:
        return False


def validate_colChoice(inp):
    # Validate column selections in search() and edit_card() functions
    valid_keys = 'islfytcvdp'
    for col in inp:
        if col not in valid_keys:
            return False
        else:
            return True


def validate_id_int(inp):
    # Validate input for ID field
    try:
        xx = int(inp)
        if xx in range(1, 1000):
            return True
        else:
            return False
    except:
        return False 


def validate_colParams(col, inp):
    # Validate search terms, here called column params
    varchars = 'slftcd'
    prices = 'vp'
    years = 'y'
    id = 'i'
    
    if col in varchars:
        if validate_varchar(inp) == True:
            return True
        else:
            return False

    elif col in years:
        if validate_year(inp) == True:
            return True
        else:
            return False

    elif col in prices:
        if validate_price(inp) == True:
            return True
        else:
            return False

    elif col in id:
        if validate_id_int(inp) == True:
            return True
        else:
            return False

    else:
        return False


def validate_operator(inp):
    # Validate the chosen operator for [y, v, d, p] columns in search()
    try:
        if inp == 'lt' or inp == 'eq' or inp == 'gt':
            return True
        else:
            return False
    except:
        return False


def confirm_commit():
    # Confirm add, update, or delete prior to committing changes
    global add_data
    global message
    
    if len(message) > 0:
        print(message)
        message = ''
    else:
        clear_screen()
    
    commit_response = input('\n Commit the above changes? [Y]es or [N]o. > ').lower()
    if commit_response == 'y':
        try:
            conn.commit()
            clear_screen()
            add_data = {}
            message = ''
            print('\n     <<< Changes committed. >>>')
            print('_' * 50)
        except:
            message = ''
            print('\n     <<< Something went wrong. Admin: See database error log. >>>')
            print('_' * 50)
    elif commit_response == 'n':
        clear_screen()
        add_data = {}
        message = ''
        print('\n     <<< The changes were not saved. >>>')
        print('_' * 50)
    else:
        clear_screen()
        add_data = {}
        message = ''
        print('\n     <<< Invalid input. No changes saved. >>>')
        print('_' * 50)
    main_menu()


#---QUERY_CONSTRUCTORS-----------------------------------------------------------------------------------------


# Required, NOT NULL columns

def input_sport():
    global add_data
    sp = remove_special(input(' Sport: ').strip().capitalize())
    while validate_varchar(sp) == False:
        print(' <<< Invalid sport >>>')
        sp = remove_special(input(' Sport: ').strip().capitalize())
    add_data.update({'sport': sp})
    return sp


def input_lastName():
    global add_data
    ln = remove_special(input(' Last Name: ').strip().capitalize())
    while validate_varchar(ln) == False:
        print(' <<< Invalid last name >>>')
        ln = remove_special(input(' Last Name: ').strip().capitalize())
    add_data.update({'lastName': ln})
    return ln


def input_firstName():
    global add_data
    fn = remove_special(input(' First Name: ').strip().capitalize())
    while validate_varchar(fn) == False:
        print(' <<< Invalid first name >>>')
        fn = remove_special(input(' First Name: ').strip().capitalize())
    add_data.update({'firstName': fn})
    return fn


def input_team():
    global add_data
    tm = remove_special(input(' Team on card: ').strip().capitalize())
    while validate_varchar(tm) == False:
        print(' <<< Invalid team >>>')
        tm = remove_special(input(' Team on card: ').strip().capitalize())
    add_data.update({'team': tm})
    return tm


def input_year():
    global add_data
    cy = remove_special(input(' Card year as yyyy: ').strip())
    if cy == 'Q' or cy == 'q':
        return 'Q'
    while validate_year(cy) == False:
        print(' <<< Invalid year >>>')
        cy = remove_special(input(' Card year as yyyy: ').strip())
        if cy == 'Q' or cy == 'q':
            return 'Q'
    add_data.update({'year': cy})
    return cy


def input_co():
    global add_data
    co = remove_special(input(' Company: ').strip().capitalize())
    while validate_varchar(co) == False:
        print(' <<< Invalid company >>>')
        co = remove_special(input(' Company: ').strip().capitalize())
    add_data.update({'company': co})
    return co


# Optional NULL columns

def input_valueEst():
    global add_data
    ve = remove_special(input(' Estimated value (Null): ').strip())
    if ve == 'Q' or ve == 'q':
        return 'Q'
    elif ve == '':
        add_data.update({'valueEst': None})
        return
    
    while ve != '' and validate_price(ve) == False:
        print(' <<< Invalid estimated value >>>')
        ve = remove_special(input(' Estimated value (Null): ').strip())
        if ve == 'Q' or ve == 'q':
            return 'Q'
    if ve == '':
        add_data.update({'valueEst': None})
        return
    else:
        add_data.update({'valueEst': ve})
        return ve


def input_saleDate():
    global add_data
    sd = remove_special(input(' Sale date as yyyy-mm-dd (Null): ').strip())
    if sd == 'Q' or sd == 'q':
        return 'Q'
    elif sd == '':
        add_data.update({'saleDate': None})
        return False
    
    while sd != '' and validate_date(sd) == False:
        print(' <<< Invalid sale date >>>')
        sd = remove_special(input(' Sale date as yyyy-mm-dd (Null): ').strip())
        if sd == 'Q' or sd == 'q':
            return 'Q'
    if sd == '':
        add_data.update({'saleDate': None})
        return False
    else:
        add_data.update({'saleDate': sd})
        return sd
    

def input_salePrice():
    global add_data
    pr = remove_special(input(' Sale price (Null): ').strip())
    if pr == 'Q' or pr == 'q':
        return 'Q'
    elif pr == '':
        add_data.update({'salePrice': None})
        return False
    
    while pr != '' and validate_price(pr) == False:
        print(' <<< Invalid sale price >>>')
        pr = remove_special(input(' Sale price (Null): ').strip())
        if pr == 'Q' or pr == 'q':
            return 'Q'
    if pr == '':
        add_data.update({'salePrice': None})
        return False
    else:
        add_data.update({'salePrice': pr})
        return pr


#---MAIN_BLOCK-------------------------------------------------------------------------------------------------


def add_card():
    # Add a card to the database, if inputs are valid
    global message
    global add_data
    clear_screen()
    print('\n Enter card values as prompted. Required unless (Null), press Enter to skip.\n')

    sp = input_sport()
    if sp == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()

    ln = input_lastName()
    if ln == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()

    fn = input_firstName()
    if fn == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()

    cy = input_year()
    if cy == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()
    
    tm = input_team()
    if tm == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()

    co = input_co()
    if co == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()
    
    ve = input_valueEst()
    if ve == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()
    
    sd = input_saleDate()
    if sd == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()
    
    pr = input_salePrice()
    if pr == 'Q':
        clear_screen()
        message = '\n     <<< Card entry canceled >>>'
        main_menu()

    message = '\n [ {} {}, {} - {} ({}) ] will be added to the database.\n'.format(fn, ln, tm, cy, co)
    
    # Build INSERT query by iterating over the 'global add_data' dict
    try:
        cur.execute(
                    """INSERT INTO public.cardinfo 
                        (sport, "lastName", "firstName", year, team, company, "valueEst", "saleDate", "salePrice")
                        VALUES
                        (%(sport)s, %(lastName)s, %(firstName)s, %(year)s, %(team)s, 
                        %(company)s, %(valueEst)s, %(saleDate)s, %(salePrice)s);""", 
                        add_data)
    except:
        clear_screen()
        print('\n     <<< Fatal error. See database logs for info. >>>\n')
        cur.close()
        conn.close()
        quit()

    # Confirm changes before committing to the database
    confirm_commit()


def search():
    # Search by up to two columns at a time
    clear_screen()
    
    global message
    global columns_actual 
    global columns_disp
    
    # Set some variables
    build_operators = []
    query_list = []

    # Begin search function with menu and input prompt
    print('\n     <<< SEARCH OPTIONS >>>')
    
    print('\n [I]D, [S]port, [L]ast name, [F]irst name, [Y]ear, [T]eam, [C]ompany,')
    print(' [V]alue est., [D]ate of sale, [P]rice, [Q]uit to Main Menu')
    print('\n Enter up to two (2) desired search fields (Example: sv ) \n')

    # Prompt for columns to search in
    col_choice = input(' >> ').replace(' ','').lower().strip()

    # Check for [Q]uit to main menu
    if 'q' in col_choice:
        clear_screen()
        message = '\n     <<< Search action canceled >>>\n'
        main_menu()
    
    # Check for empty column input
    if col_choice == '':
            clear_screen()
            message = '\n     <<< Empty column input >>>\n'
            main_menu()
    
    # Make sure only 1 or 2 columns are elected
    if len(col_choice) > 2:
        clear_screen()
        message = '\n     <<< Invalid column input >>>\n'
        main_menu()
    elif len(col_choice) == 2:
        if col_choice[0] == col_choice[1]:
            clear_screen()
            message = '\n     <<< Invalid column input >>>\n'
            main_menu()

    clear_screen()
    
    # Validate column choices
    for col in col_choice:
        if validate_colChoice(col) == False:
            clear_screen()
            message = '\n     <<< Invalid column input >>>\n'
            main_menu()

    # If column is among dynamically searchable fields, give 'lt, gt, eq' options
    for col in col_choice:
        if col in 'iyvdp':
            print('\n Optional: Precede search term by [lt, gt, eq] for less than, greater than, equals. Default is eq.')
            print('\n Recall that dates follow a yyyy-mm-dd format.')
            s_term = remove_special(input('\n Enter search term for ' + columns_disp[col] + ': ').lower().strip())
            
            # Check for empty input
            if s_term == '' or len(s_term) == 0:
                clear_screen()
                message = '\n     <<< Empty search terms >>>'
                main_menu()
            
            # Extract the first two chars to see if they are 'lt, gt, eq' operators
            check_ops = s_term[0] + s_term[1] if len(s_term) > 1 else s_term[0]
            s_term2 = s_term[2:] if len(s_term) >= 2 and str(s_term[0:2]) in 'ltgteq' else s_term

            # Add 'lt, gt, eq' operators to build_operators if given as input
            if validate_operator(check_ops) == True:
                if check_ops == 'lt':
                    build_operators.append('<')
                elif check_ops == 'eq':
                    build_operators.append('=')
                elif check_ops == 'gt':
                    build_operators.append('>')
            # Otherwise, add the default '=' to build_operators
            else:
                build_operators.append('=')
            
            # Validate search terms for 'iyvdp' column
            if validate_colParams(col, s_term2) == True:
                query_list.append((columns_actual[col], s_term2))
            else:
                clear_screen()
                message = '\n     <<< Invalid search terms >>>'
                main_menu()
                
        # Or, if columns selected are varchar fields, accept input, strip spaces and specials, validate
        else:
            s_term = remove_special(input('\nEnter search term for ' + columns_disp[col] + ': ').lower().strip())
            if s_term == 'q':
                clear_screen()
                message = '\n     <<< Search action canceled >>>'
                main_menu()
            elif s_term == '' or len(s_term) == 0:
                clear_screen()
                message = '\n     <<< Empty search terms >>>'
                main_menu()
            elif validate_colParams(col, s_term) == True:
                query_list.append((columns_actual[col], '%' + s_term + '%'))
                build_operators.append('ILIKE')
            else:
                clear_screen()
                message = '\n     <<< Invalid search terms >>>'
                main_menu()


    # Columns and search terms are valid, build search query
    if len(col_choice) == 1:
        s_query = """SELECT * FROM public.cardinfo WHERE "{}" {} '{}';"""\
        .format(query_list[0][0], build_operators[0], query_list[0][1])
        build_operators = []
        query_list = []
    elif len(col_choice) == 2:
        s_query = """SELECT * FROM public.cardinfo WHERE "{}" {} '{}' AND "{}" {} '{}';"""\
        .format(query_list[0][0], build_operators[0], query_list[0][1], query_list[1][0], build_operators[1], query_list[1][1])
        build_operators = []
        query_list = []

    # Execute search query, store some variables about number of rows that match
    try:
        cur.execute(s_query)
    except:
        clear_screen()
        print('\n     <<< Fatal error. See the database logs for info. >>>\n')
        cur.close()
        conn.close()
        quit()

    results = cur.fetchmany(10)
    total = cur.fetchall()
    
    current_rows = len(results)
    total_rows = len(total) + 10
    
    # Clear screen and prepare to display search results
    clear_screen()
    
    print('\n     <<< Search complete! >>>')
    
    if current_rows > 1 and current_rows <= 10 and total_rows == 10:
        print('\n     ' + str(current_rows) + ' rows returned (max 10)')
    elif total_rows > 10:
        print('\n     ' + str(current_rows) + ' rows returned (max 10) of ' + str(total_rows) + ' that match search criteria.')
    elif current_rows == 0:
        print('\n     <<< No results match the query. >>>\n')
        main_menu()
    
    # Build table of search results
    res = tt.Texttable()
    header = ['ID', 'Sport', 'Last name', 'First name', 'Year', 'Team', 'Co.', 'Est. Value', 'Sale date', 'Sale price']
    res.header(header)
    res.set_cols_width([4, 10, 10, 10, 6, 10, 10, 8, 10, 8])
    res.set_cols_align(['c']*10)
    res.set_cols_valign(['m']*10)
    res.set_chars(['-','|','+','='])

    # Print the table to the screen
    if len(results) != 0:
        print('\n')
        for row in results:
            res.add_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]])
        results_table = res.draw()
        print(results_table)

    main_menu()


def edit_card():
    # Prompt for new value, validate
    global message
    global columns_actual
    global columns_disp

    # Display the edit menu
    clear_screen()
    print('\n     <<< EDIT OPTIONS >>>')
    id_choice = remove_special(input('\n Enter \'ID\' of card you wish to edit: ').replace(' ','').lower().strip())
    if validate_id_int(id_choice) == True:
        id_query = """SELECT * FROM public.cardinfo WHERE "ID" = {};""".format(id_choice)
    else:
        clear_screen()
        print('\n     <<< Invalid ID >>>')
        main_menu()

    # Execute search by ID query, return the one result
    cur.execute(id_query)
    results = cur.fetchone()
    
    # Check to see if given ID matches a card in the database
    try:
        aa = len(results)
    except:
            clear_screen()
            print('\n     <<< No card with that ID exists. >>>\n')
            main_menu()

    # Build table of search results
    res = tt.Texttable()
    header = ['ID', 'Sport', 'Last name', 'First name', 'Year', 'Team', 'Co.', 'Est. Value', 'Sale date', 'Sale price']
    res.header(header)
    res.set_cols_width([4, 10, 10, 10, 6, 10, 10, 8, 10, 8])
    res.set_cols_align(['c']*10)
    res.set_cols_valign(['m']*10)
    res.set_chars(['-','|','+','='])

    # Print results table
    print('\n')
    res.add_row([results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7], results[8], results[9]])
    results_table = res.draw()
    print(results_table)

    # Prompt for column to edit
    print('\n [I]D, [S]port, [L]ast name, [F]irst name, [Y]ear, [T]eam, [C]ompany,')
    print(' [V]alue est., [D]ate of sale, [P]rice, [Q]uit to Main Menu')
    ecol_choice = remove_special(input('\n Select the field you wish to edit: ').replace(' ','').lower().strip())

    # Validate column choice
    if ecol_choice == 'q':
        clear_screen()
        message = '\n     <<< Edit action canceled >>>\n'
        main_menu()
    elif ecol_choice == 'i':
        clear_screen()
        message = '\n     <<< Cannot edit ID field >>>\n'
        main_menu()
    elif validate_colChoice(ecol_choice) == False:
        clear_screen()
        message = '\n     <<< Invalid column input >>>\n'
        main_menu()
    elif validate_colChoice(ecol_choice) == True:

        # Check if desired edit column is in a date or int field
        if ecol_choice in 'yvdp':
            edit = remove_special(input('\n Enter new value for \'' + columns_disp[ecol_choice] + '\': ').strip().lower())
            if edit == len(edit) == 0:
                clear_screen()
                message = '\n     <<< Empty input >>>\n'
                main_menu()
            elif edit == 'q':
                clear_screen()
                message = '\n     <<< Edit action canceled >>>\n'
                main_menu()
            elif ecol_choice == 'd':
                if validate_date(edit) == False:
                    clear_screen()
                    message = '\n     <<< Invalid date >>>\n'
                    main_menu()
            elif ecol_choice == 'y':
                if validate_year(edit) == False:
                    clear_screen()
                    message = '\n     <<< Invalid year >>>\n'
                    main_menu()
            elif ecol_choice in 'v':
                if validate_price(edit) == False:
                    clear_screen()
                    message = '\n     <<< Invalid value >>>\n'
                    main_menu()
            elif ecol_choice in 'p':
                if validate_price(edit) == False:
                    clear_screen()
                    message = '\n     <<< Invalid price >>>\n'
                    main_menu()

        # Otherwise accept and validate varchar
        else:
            edit = remove_special(input('\n Enter new value for ' + columns_disp[ecol_choice] + ': ').strip().capitalize())
            if edit == 'Q':
                clear_screen()
                message = '\n     <<< Edit action canceled >>>\n'
                main_menu()
            elif validate_varchar(edit) == False:
                clear_screen()
                message = '\n     <<< Invalid input >>>\n'
                main_menu()

    # Build query and execute
    e_query = """UPDATE public.cardinfo SET "{}" = '{}' WHERE "ID" = {};""".format(columns_actual[ecol_choice], edit, id_choice)

    message = '\n At card ID: {}, \'{}\' will be updated to \'{}.\''.format(id_choice, columns_disp[ecol_choice], edit)

    try:
        cur.execute(e_query)
    except:
        clear_screen()
        print('\n     <<< Fatal error. See database logs for info. >>>\n')
        cur.close()
        conn.close()
        quit()
        #conn.rollback()
        #clear_screen()
        #message = '\n     <<< Query not successful. >>>\n'
        #main_menu()
    
    confirm_commit()


def vend_card():
    # Vend / sell a card by ID
    
    global message
    
    clear_screen()
    print('\n     <<< VEND OPTIONS >>>')
    id_choice = remove_special(input('\n Enter \'ID\' of card you wish to vend: ').replace(' ','').lower().strip())
    if validate_id_int(id_choice) == True:
        id_query = """SELECT * FROM public.cardinfo WHERE "ID" = {};""".format(id_choice)
    elif id_choice == 'q':
        clear_screen()
        print('\n     <<< Vend action canceled >>>')
        main_menu()
    else:
        clear_screen()
        print('\n     <<< Invalid ID >>>')
        main_menu()

    # Execute search by ID query, return the one result
    cur.execute(id_query)
    results = cur.fetchone()
    
    # Check to see if given ID matches a card in the database
    try:
        aa = len(results)
    except:
            clear_screen()
            print('\n     <<< No card with that ID exists. >>>\n')
            main_menu()

    # Build table of search results
    res = tt.Texttable()
    header = ['ID', 'Sport', 'Last name', 'First name', 'Year', 'Team', 'Co.', 'Est. Value', 'Sale date', 'Sale price']
    res.header(header)
    res.set_cols_width([4, 10, 10, 10, 6, 10, 10, 8, 10, 8])
    res.set_cols_align(['c']*10)
    res.set_cols_valign(['m']*10)
    res.set_chars(['-','|','+','='])

    # Print results table
    print('\n')
    res.add_row([results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7], results[8], results[9]])
    results_table = res.draw()
    print(results_table)
    
    # Prompt for saleDate and salePrice values
    print('\n')
    
    v_date = input_saleDate()
    if v_date == 'q' or v_date == 'Q':
        clear_screen()
        message = '\n     <<< Card sale canceled >>>'
        main_menu()
    elif v_date == False:
        clear_screen()
        message = '\n     <<< Invalid sale date input >>>'
        main_menu()

    print('\n')
    
    s_price = input_salePrice()
    if s_price == 'q' or s_price == 'Q':
        clear_screen()
        message = '\n     <<< Card sale canceled >>>'
        main_menu()
    elif s_price == False:
        clear_screen()
        message = '\n     <<< Invalid sale price >>>'
        main_menu()
    
    print('\n')
    
    # Summary of card to be sold
    message = 'The card at ID {} was sold on {} for a price of ${}.'.format(id_choice, v_date, s_price)
    
    # UPDATE query
    v_query = """UPDATE public.cardinfo SET "saleDate" = '{}', "salePrice" = {} WHERE "ID" = {};""".format(v_date, s_price, id_choice)

    try:
        cur.execute(v_query)
    except:
        clear_screen()
        print('\n     <<< Fatal error. See the database logs for info. >>>\n')
        cur.close()
        conn.close()
        quit()
    
    confirm_commit()


def delete_card():
    # Delete a card by ID
    
    global message
    
    clear_screen()
    print('\n     <<< DELETE OPTIONS >>>')
    id_choice = remove_special(input('\n Enter \'ID\' of card you wish to delete: ').replace(' ','').lower().strip())
    if validate_id_int(id_choice) == True:
        id_query = """SELECT * FROM public.cardinfo WHERE ID = {};""".format(id_choice)
    elif id_choice == 'q':
        clear_screen()
        print('\n     <<< Delete action canceled >>>')
        main_menu()
    else:
        clear_screen()
        print('\n     <<< Invalid ID >>>')
        main_menu()

    # Execute search by ID query, return the one result
    cur.execute(id_query)
    results = cur.fetchone()
    
    # Check to see if given ID matches a card in the database
    try:
        aa = len(results)
    except:
            clear_screen()
            print('\n     <<< No card with that ID exists. >>>\n')
            main_menu()

    # Build table of search results
    res = tt.Texttable()
    header = ['ID', 'Sport', 'Last name', 'First name', 'Year', 'Team', 'Co.', 'Est. Value', 'Sale date', 'Sale price']
    res.header(header)
    res.set_cols_width([4, 10, 10, 10, 6, 10, 10, 8, 10, 8])
    res.set_cols_align(['c']*10)
    res.set_cols_valign(['m']*10)
    res.set_chars(['-','|','+','='])

    # Print results table
    print('\n')
    res.add_row([results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7], results[8], results[9]])
    results_table = res.draw()
    print(results_table)
    
    # Summary of card to be deleted
    message = '\n The card at ID {} will be PERMANENTLY DELETED from the database.'.format(id_choice)
    
    # DELETE query
    d_query = """DELETE from public.cardinfo WHERE id = {};""".format(id_choice)

    try:
        cur.execute(d_query)
    except:
        clear_screen()
        print('\n     <<< Fatal error. See the database logs for info. >>>\n')
        cur.close()
        conn.close()
        quit()
    
    confirm_commit()
    

#---END_CLOSE--------------------------------------------------------------------------------------------------


def quit_carddb():
    clear_screen()
    confirm_quit = input('\n Exit the program and close database connection? [Y]es or [N]o. ').lower()
    if confirm_quit == 'y':
        cur.close()
        conn.close()
        quit()
    elif confirm_quit == 'n':
        clear_screen()
        main_menu()
    else:
        clear_screen()
        print('\n     <<< Invalid response >>>\n')
        print('_' * 50)
        main_menu()


# Initialize functional program
main_menu()
