import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import Series, DataFrame


# conversion
eV = 27.2114

# The input file is read line by line, the first line of the input express if the Plot will be the DOS 
# of a single file or the comparison of multiple files. The second line tells to the software if the DOS
# from an open shell or a closed calculation. The third line expresses the plotting mode.
# If the plot is the comparison of multiple DOS from the fourthline all the .doss/.f24 file path needed, 
# the section is ended by the keyword end. If the plot is a single DOS the fourth line is the file path 
# of .doss/.f24 needed. Once the counter gets to 4 all the following lines are occupied by the labels 
# for the plot. 
reference = input("Introduce your input file: \n")
reference = open(reference, 'r')
count = 0
check = True
check2 = True
file_list = []
labels = []
adm_key_file = ['SINGLE', 'MULTIPLE']
adm_key_shell = ['CLOSED', 'OPEN']
adm_key_plot=['OVERLAP', 'OPPOSITE','NONE']
while check == True:
    line = reference.readline()
    fine = len(line)
    save_el = line[0:fine-1]
    if count == 0:
        # Flag for single or multiple files if you have only one file write SINGLE else write MULITPLE
        file_number = save_el
        if file_number not in adm_key_file:
            print("Error: The keyword "+file_number+" is not admissible")
            exit()

    elif count == 1:
        # Define if the input file is the result of a Closed shell or an Open shell calculation
        shell = save_el  
        if shell not in adm_key_shell:
            print("Error: The keyword "+shell+" is not admissible")
            exit()

    elif count==2:
        # This keyword has to be NONE if the plot is from a closed shell calculation, it can be OVERLAP or OPPOSITE if 
        # the DOS is from an open shell calculation
        plot_mode=save_el
        if plot_mode not in adm_key_plot:
            print('Error: The keyword '+plot_mode+'is not admissible')
            exit()

    elif count == 3 and file_number == 'MULTIPLE':
        while check2 == True:
            if save_el != 'end':  # readout of the .doss/.f24 path file needed
                file_list.append(save_el)
                line=reference.readline()
                fine=len(line)
                save_el=line[0:fine-1]
            else:
                check2 = False

    elif count == 3 and file_number == 'SINGLE':
        file_list.append(save_el) # readout of the .doss/.f24 path file needed

    else:
        save_el = line[0:fine]
        if save_el != 'end':
            labels.append(save_el)
        else:
            check = False
    count += 1
    

def closed_shell_read(file_input, labels):
    # Determination of the skiprow parameter, the skiprow parameter is needed to avoid the header when reading the 
    # .doss/.f24 file with the pd.read_csv instruction
    headers = ['#', '@']
    skiprow = 0
    file_pandas = file_input
    file_input = open(file_input, 'r')
    file_fermi=file_input
    check1 = True
    while check1 == True:
        line = file_input.readline()
        if line[0] in headers:
            skiprow += 1
        else:
            file_input.close()
            check1 = False

    # Determination of the fermi energy
    file_fermi=open(file, 'r')
    lines=file_fermi.read().splitlines()
    fermi_energy=lines[-1]
    fermi_energy=fermi_energy.split()
    fermi_energy=float(fermi_energy[3])
    fermi_energy=fermi_energy*eV
    
    # creation of the DataFrame
    Dos = pd.read_csv(file_pandas, sep="\s+", header=None,
                      engine='python', skiprows=skiprow, skipfooter=1)
    No_projections = len(Dos.columns)-1

    # Error check: number of labels has to be equal to the number of images required
    if len(labels) != No_projections:
        print('Error: The number of labels you have inserted does not match the number of projections required')
        exit()

    return Dos, No_projections, fermi_energy


def open_shell_read(file_input, labels):
    # Determination of the skiprow and skiprow2 parameters, the skiprow parameter is needed to avoid the header when reading the 
    # .doss/.f24 file with the pd.read_csv command, the skiprow2 parameter has the same function of skiprow and it is needed because 
    # alpha and beta spin data are held in the same file
    headers = ['#', '@']
    skiprow = 0
    skiprow2 = 0
    file_pandas = file_input
    file_input = open(file_input, 'r')
    file_fermi=file_input
    check1 = True
    while check1 == True:
        line = file_input.readline()
        if line[0] in headers:
            skiprow += 1
            skiprow2 += 1
        elif line[0] == '&':
            skiprow -= 1
            skiprow2 += 1
            file_input.close()
            check1 = False
        else:
            skiprow2 += 1

    # determination of the skipfoot parameter, is needed when reading the alpha data with the pd.read_csv instruction to avoid the
    # beta spin data
    skipfoot = skiprow2-skiprow+1

    #Determination of the fermi energy
    file_fermi=open(file, 'r')
    lines=file_fermi.read().splitlines()
    fermi_energy=lines[-1]
    fermi_energy=fermi_energy.split()
    fermi_energy=float(fermi_energy[3])
    fermi_energy=fermi_energy*eV

    # Creation of alpha and beta spin parameter
    Dos_alpha = pd.read_csv(file_pandas, sep="\s+", header=None,
                            engine='python', skiprows=skiprow, skipfooter=skipfoot)
    Dos_beta = pd.read_csv(file_pandas, sep="\s+", header=None,
                           engine='python', skiprows=skiprow2, skipfooter=1)

    # Number of projection for spin alpha and spin beta
    No_projections_alpha = len(Dos_alpha.columns)-1
    No_projections_beta = len(Dos_beta.columns)-1

    # Error check: number of projections for spin alpha and spin beta has to be equal
    if No_projections_alpha != No_projections_beta:
        print('Error: The number of projections required for spin alpha and spin beta are different')
        exit()

    # Error check: the number of labels introduced has to be equal to the number of projections required
    if len(labels) != No_projections_alpha:
        print('Error: The number of labels you have inserted does not match the number of projections required')
        exit()

    return Dos_alpha, Dos_beta, No_projections_alpha, No_projections_beta, fermi_energy


def compare_closed_shell_file_read(file_input, labels):
    # Determination of the skiprow parameter, the skiprow parameter is needed to avoid the header when reading the 
    # .doss/.f24 file with the pd.read_csv instruction, in order to read all the files needed, to do so the files are
    # dealth as a list
    No_projections = []
    Dos_list = []
    fermi_list=[]
    file_list=file_input
    for i in range(0, len(file_input)):
        # determination of skiprow
        headers = ['#', '@']
        skiprow = 0
        file_pandas = file_list[i]
        file_fermi=file_list[i]
        file_input = open(file_list[i], 'r')
        ceck = True
        while ceck == True:
            line = file_input.readline()
            if line[0] in headers:
                skiprow += 1
            else:
                file_input.close()
                ceck = False

         #Determination of the fermi energy
        file_fermi=open(file_fermi, 'r')
        lines=file_fermi.read().splitlines()
        fermi_energy=lines[-1]
        fermi_energy=fermi_energy.split()
        fermi_energy=float(fermi_energy[3])
        fermi_energy=fermi_energy*eV
        fermi_list.append(fermi_energy)

        # data import
        Dos_list.append(pd.read_csv(
            file_pandas, sep="\s+", header=None, engine='python', skiprows=skiprow, skipfooter=1))
        No_projections.append(len(Dos_list[i].columns)-1)

    # Error check: All the file imported should have the same number of projections
    projection_reference = No_projections[0]
    for i in range(0, len(No_projections)):
        k = No_projections[i]
        if k != projection_reference:
            print(
                'Error: The file imported do not require the same number of projections', i)
            exit()

    # Error check: The total number of labels has to be equal to the sum of columns in the database
    Number_of_lines = No_projections[0]*len(No_projections)
    if len(labels) != Number_of_lines:
        if len(labels) > Number_of_lines:
            print('Error: You have more labels than lines')
            exit()
        elif len(labels) < Number_of_lines:
            print('Error: You do not have enough labels')
            exit()

    return Dos_list, No_projections, fermi_list


def compare_open_shell_file_read(file_input, labels):
    # Determination of the skiprow and skiprow2 parameters, the skiprow parameter is needed to avoid the header when reading the 
    # .doss/.f24 file with the pd.read_csv command, the skiprow2 parameter has the same function of skiprow and it is needed because 
    # alpha and beta spin data are held in the same file. In order to read all the files needed, to do so the files are
    # dealth as a list
    No_projections_alpha = []
    No_projections_beta = []
    Dos_list_alpha = []
    Dos_list_beta = []
    fermi_list=[]
    file_list=file_input
    for i in range(0, len(file_input)):
        #determination skiprow1 and skiprow2 parameter
        headers = ['#', '@']
        skiprow = 0
        skiprow2 = 0
        file_pandas = file_list[i]
        file_fermi=file_list[i]
        file_input = open(file_list[i], 'r')
        check1 = True
        while check1 == True:
            line = file_input.readline()
            if line[0] in headers:
                skiprow += 1
                skiprow2 += 1
            elif line[0] == '&':
                skiprow -= 1
                skiprow2 += 1
                file_input.close()
                check1 = False
            else:
                skiprow2 += 1

        # determination of the skipfoot parameter
        skipfoot = skiprow2-skiprow+1

        #Determination of the fermi energy
        file_fermi=open(file_fermi, 'r')
        lines=file_fermi.read().splitlines()
        fermi_energy=lines[-1]
        fermi_energy=fermi_energy.split()
        fermi_energy=float(fermi_energy[3])
        fermi_energy=fermi_energy*eV
        fermi_list.append(fermi_energy)

        # Data import
        Dos_list_alpha.append(pd.read_csv(file_pandas, sep="\s+", header=None,
                                        engine='python', skiprows=skiprow, skipfooter=skipfoot))
        Dos_list_beta.append(pd.read_csv(file_pandas, sep="\s+", header=None,
                                       engine='python', skiprows=skiprow2, skipfooter=1))

        # Number of projection for spin alpha and spin beta
        No_projections_alpha.append(len(Dos_list_alpha[i].columns)-1)
        No_projections_beta.append(len(Dos_list_beta[i].columns)-1)

    # Error check: The number of projections for each spin alpha and spin beta should the same
    projection_reference_alpha = No_projections_alpha[0]
    projection_reference_beta = No_projections_beta[0]

    # Check on alpha
    for i in range(0, len(No_projections_alpha)):
        k = No_projections_alpha[i]
        if k != projection_reference_alpha:
            print(
                'Error: The file imported for spin \u03B1 do not require the same number of projections', i)
            exit()

    # Check on beta
    for i in range(0, len(No_projections_beta)):
        k = No_projections_beta[i]
        if k != projection_reference_beta:
            print(
                'Error: The file imported for spin \u03B2 do not require the same number of projections', i)
            exit()

    # Cross check
    if projection_reference_alpha != projection_reference_beta:
        print('Error: The number of projection required by spin \u03B1 file differs from the one required by spin \u03B2')

    # Error check: The total number of labels has to be equal to the sum of columns in the database
    Number_of_lines = No_projections_alpha[0]*len(No_projections_alpha)
    if len(labels) != Number_of_lines:
        if len(labels) > Number_of_lines:
            print('Error: You have more labels than lines')
            exit()
        elif len(labels) < Number_of_lines:
            print('Error: You do not have enough labels')
            exit()

    return Dos_list_alpha, Dos_list_beta, No_projections_alpha, No_projections_beta, fermi_list


def closed_shell_plot(dataset, number_of_projections, Fermi, labels):
    # Creation of lists to collect the maximum and minimum of DOS to plot the Fermi level 
    y_mx = []
    y_mn = []
    # Definition of x coordinates of the Fermi level
    x_fermi = np.zeros(2)
    # Creation of the vector needed to subtract the Fermi energy from all the energies vector
    fermi_level=(dataset[0]/dataset[0])*Fermi
    dx = dataset[0]*eV-fermi_level
    # Calculation of the maximum and minimum energies to set the limit on x axes
    x_mn = min(dx)
    x_mx = max(dx)
    for i in range(1, number_of_projections+1):
        dy = dataset[i]
        maxy = dy.max()
        miny = dy.min()
        y_mx.append(maxy)
        y_mn.append(miny)

    # creation of plot
    if number_of_projections!=1:
        # Creation of the figure and the matrix of subplots that has the dimension of nrows and n columns 
        fig, axs = plt.subplots(nrows=number_of_projections,
                                ncols=1, sharex=True, figsize=(6, 9))
        for i in range(1, number_of_projections+1):
            # Plotting of all the sublplots
            k = i-1
            axs[k].plot(dx, dataset[i], color='red')
            y_fermi = np.linspace(y_mn[k]-2, y_mx[k]+2, 2)
            axs[k].plot(x_fermi, y_fermi, color='blue')
            axs[k].set_xlim([x_mn, x_mx])
            fig.text(0.06, 0.5, 'DOS (a.u.)', ha='center',
             va='center', rotation='vertical')

    # Creation of the plot when only the total projection is required without any subplots 
    elif number_of_projections==1:
        fig=plt.figure()
        plt.plot(dx,dataset[1],color='red')
        y_fermi=np.linspace(y_mn[0]-2,y_mx[0]+2,2)
        plt.plot(x_fermi,y_fermi,color='blue')
        plt.xlim([x_mn,x_mx])
        plt.ylim([y_mn[0]-1,y_mx[0]+1])
        plt.ylabel('DOS (a.u)')

    plt.xlabel('Energy (eV)')
    
    plt.show()


def open_shell_plot(dataset1, dataset2, number_of_projections1, number_of_projections2, Fermi, labels):
    # Creation of lists to collect the maximum and minimum of DOS to plot the Fermi level both for alpha and beta spin
    y_mx_alpha = []
    y_mn_alpha = []
    y_mx_beta = []
    y_mn_beta = []
    # Definition of x coordinates of the Fermi level
    x_fermi = np.zeros(2)
    # Creation of the vector needed to subtract the Fermi energy from all the energies vector
    fermi_level=(dataset1[0]/dataset1[0])*Fermi
    dx_alpha = dataset1[0]*eV-fermi_level
    dx_beta = dataset2[0]*eV-fermi_level
    # Calculation of the maximum and minimum energies to set the limit on x axes
    x_mn = min(dx_alpha)
    x_mx = max(dx_beta)
    y_zero = np.zeros(2)
    for i in range(1, number_of_projections1+1):
        dy_alpha = dataset1[i]
        dy_beta = dataset2[i]
        maxy = dy_alpha.max()
        miny = dy_alpha.min()
        y_mx_alpha.append(maxy)
        y_mn_alpha.append(miny)
        maxy = dy_beta.max()
        miny = dy_beta.min()
        y_mx_beta.append(maxy)
        y_mn_beta.append(miny)

    # creation of plot
    if number_of_projections1!=1:
        # Creation of the figure and the matrix of subplots that has the dimension of nrows and ncolumns 
        fig, axs = plt.subplots(nrows=number_of_projections1,
                                ncols=1, sharex=True, figsize=(6, 9))
        for i in range(1, number_of_projections1+1):
            # Plotting of all the sublplots
            k = i-1
            axs[k].plot(dx_alpha, dataset1[i], color='red',
                        label=labels[k]+' \u03B1')

            # Plotting option for the plot mode OPPOSITE
            if plot_mode=='OPPOSITE':
                axs[k].plot(dx_beta, dataset2[i], color='red',linestyle=('dashed'), label=labels[k]+' \u03B2')
                y_mn = min(y_mn_beta)

            # Plotting option for the plot mode OVERLAP
            elif plot_mode=='OVERLAP':
                axs[k].plot(dx_beta, -dataset2[i], color='red',linestyle=('dashed'), label=labels[k]+' \u03B2')
                y_mn = min(y_mn_alpha)

            y_mx = max(y_mx_alpha)

            y_fermi = np.linspace(y_mn-6, y_mx+6, 2)
            axs[k].plot(x_fermi, y_fermi, color='blue')
            axs[k].set_xlim([x_mn, x_mx])
            axs[k].set_ylim([y_mn-5, y_mx+5])
            axs[k].legend()

            #Zero DOS line plot
            if plot_mode=='OPPOSITE':
                x_zero = np.linspace(x_mn, x_mx, 2)
                axs[k].plot(x_zero, y_zero, color='black')
                

        fig.text(0.06, 0.5, 'DOS (a.u.)', ha='center',
             va='center', rotation='vertical')
        
    # Creation of the plot when only the total projection is required without any subplots 
    elif number_of_projections1==1:
        fig=plt.figure()
        plt.plot(dx_alpha,dataset1[i],color='red', label=labels[0]+' \u03B1')

        # Plotting option for the plot mode OPPOSITE
        if plot_mode=='OPPOSITE':
            plt.plot(dx_beta,dataset2[i],color='red',linestyle='dashed',label=labels[0]+' \u03B2')
            y_mn=min(y_mn_beta)

        # Plotting option for the plot mode OVERLAP
        elif plot_mode=='OVERLAP':
            plt.plot(dx_beta,dataset2[i],color='red',linestyle='dashed',label=labels[0]+' \u03B2')
            y_mn=min(y_mn_alpha)

        y_mx=max(y_mx_alpha)

        y_fermi=np.linspace(y_mn-6,y_mx+6, 2)

        plt.plot(x_fermi,y_fermi,color='blue')
        plt.xlim([x_mn,x_mx])
        plt.ylim([y_mn,y_mx])

        #Zero DOS line plot
        if plot_mode=='OPPOSITE':
            x_zero=np.linspace(x_mn,x_mx,2)
            plt.plot(x_zero,y_zero,color='black')
        
        plt.legend()
        plt.ylabel('DOS (a.u)')

    plt.xlabel('Energy (eV)')
    

    plt.show()


def compare_closed_shell_plot(dataset_list, number_of_projections_list, Fermi, labels):
    color_list = ['red','darkred', 'firebrick',
                  'indianred', 'tomato', 'sienna', 'chocolate', 'peru']
    # Creation of lists to collect the maximum and minimum of DOS to plot the Fermi level 
    y_mx = []
    y_mn = []
    # Creation of lists to collect the maximum and minimum in energy of each file
    x_min = []
    x_max = []
    # Definition of x coordinates of the Fermi level
    x_fermi = np.zeros(2)
    # Creation of a list to collect the energies of each file corrected for the Fermi energy of the calculation
    dx_fermi=[]
    for i in range(0, len(dataset_list)):
        k = dataset_list[i]
        # Creation of the vector needed to subtract the Fermi energy from all the energies vector
        fermi_level=(k[0]/k[0])*Fermi[i]
        dx = k[0]*eV-fermi_level
        dx_fermi.append(dx)
        # Calculation of the maximum and minimum energies to set the limit on x axes
        x_min.append(min(dx))
        x_max.append(max(dx))
        for p in range(1, number_of_projections_list[i]+1):
            dy = k[p]
            maxy = dy.max()
            miny = dy.min()
            y_mx.append(maxy)
            y_mn.append(miny)

    x_mn = min(x_min)
    x_mx = max(x_max)
    number_of_projections = max(number_of_projections_list)

    # creation of plot
    if number_of_projections!=1:
        # Creation of the figure and the matrix of subplots that has the dimension of nrows and ncolumns 
        fig, axs = plt.subplots(nrows=number_of_projections,
                                ncols=1, sharex=True, figsize=(6, 9))
        for p in range(0, len(dataset_list)):
            dataset = dataset_list[p]
            for i in range(1, number_of_projections+1):
                k = i-1
                if p != 0:
                    axs[k].plot(dx_fermi[p], dataset[i],
                                color=color_list[p], label=labels[k*p])
                elif p == 0:
                    axs[k].plot(dx_fermi[p], dataset[i],
                                color=color_list[p], label=labels[k])

        y_fermi = np.linspace(min(y_mn)-4, min(y_mx)+4, 2)

        for k in range(0,number_of_projections):   
            
            axs[k].plot(x_fermi, y_fermi, color='blue')

            axs[k].set_xlim([x_mn, x_mx])
            axs[k].set_ylim([min(y_mn)-3,max(y_mx)+3])
            axs[k].legend()

        fig.text(0.06, 0.5, 'DOS (a.u.)', ha='center',
             va='center', rotation='vertical')

    # Creation of the plot when only the total projection is required without any subplots 
    elif number_of_projections==1:
        fig=plt.figure()
        for p in range(0,len(dataset_list)):
            dataset=dataset_list[p]
            plt.plot(dx_fermi[p],dataset[1], color=color_list[p], label=labels[p])
        y_fermi=np.linspace(min(y_mn)-4,max(y_mx)+4,2)
        plt.plot(x_fermi,y_fermi,color='blue')
        plt.xlim([x_mn,x_mx])
        plt.ylim([0,max(y_mx)+3])


    plt.xlabel('Energy (eV)')
    plt.ylabel('DOS (a.u)')
    plt.legend()
    

    plt.show()


def compare_open_shell_plot(dataset_list1, dataset_list2, number_of_projections_list1, number_of_projections_list2, Fermi, labels):
    color_list = ['red','darkred', 'firebrick',
                  'indianred', 'tomato', 'sienna', 'chocolate', 'peru']
    # Creation of lists to collect the maximum and minimum of DOS to plot the Fermi level for both alpha and beta spin
    y_mx_alpha = []
    y_mn_alpha = []
    y_mx_beta = []
    y_mn_beta = []
    # Creation of lists to collect the maximum and minimum in energy of each file
    x_max = []
    x_min = []
    # Creation of a list to collect the energies of each file corrected for the Fermi energy of the calculation
    dx_fermi_alpha=[]
    dx_fermi_beta=[]
    # Definition of x coordinates of the Fermi level and the y coordinates for the zero DOS line
    y_zero = np.zeros(2)
    x_fermi = np.zeros(2)
    for i in range(0, len(dataset_list1)):
        alpha = dataset_list1[i]
        beta = dataset_list2[i]
        # Creation of the vector needed to subtract the Fermi energy from all the energies vector
        fermi_level=(alpha[0]/alpha[0])*Fermi[i]
        dx_alpha = alpha[0]*eV-fermi_level
        dx_beta = beta[0]*eV-fermi_level
        dx_fermi_alpha.append(dx_alpha)
        dx_fermi_beta.append(dx_beta)
        # Calculation of the maximum and minimum energies to set the limit on x axes
        x_min.append(min(dx_beta))
        x_max.append(max(dx_alpha))
        for p in range(1, number_of_projections_list1[i]+1):
            dy_alpha = alpha[p]
            dy_beta = beta[p]
            maxy = dy_alpha.max()
            miny = dy_alpha.min()
            y_mx_alpha.append(maxy)
            y_mn_alpha.append(miny)
            maxy = dy_beta.max()
            miny = dy_beta.min()
            y_mx_beta.append(maxy)
            y_mn_beta.append(miny)

    x_mn = min(x_min)
    x_mx = max(x_max)
    number_of_projections1 = number_of_projections_list1[i]

    # creation of plot
    if number_of_projections1!=1:
        # Creation of the figure and the matrix of subplots that has the dimension of nrows and ncolumns 
        fig, axs = plt.subplots(nrows=number_of_projections1,
                                ncols=1, sharex=True, figsize=(6, 9))
        for p in range(0, len(dataset_list1)):
            dataset1 = dataset_list1[p]
            dataset2 = dataset_list2[p]
            for i in range(1, number_of_projections1+1):
                k=i-1
                j=i+len(dataset_list1)
                if p != 0:
                    axs[k].plot(dataset1[0], dataset1[i],
                                color=color_list[p], label=labels[j]+' \u03B1')

                    # Plotting option for the plot mode OPPOSITE
                    if plot_mode=='OPPOSITE':
                        axs[k].plot(dataset2[0], dataset2[i], color=color_list[p],linestyle=('dashed'), label=labels[j]+' \u03B2')
                        y_mn = min(y_mn_beta)

                    # Plotting option for the plot mode OVERLAP
                    elif plot_mode=='OVERLAP':
                        axs[k].plot(dataset2[0], -dataset2[i], color=color_list[p],linestyle=('dashed'), label=labels[j]+' \u03B2')
                        y_mn = min(y_mn_alpha)

                    y_mx = max(y_mx_alpha)

                    # Fermi level plot
                    y_fermi = np.linspace(y_mn-6, y_mx+6, 2)
                    axs[k].plot(x_fermi, y_fermi, color='blue')

                elif p == 0:
                    axs[k].plot(dataset1[0], dataset1[i],
                                color=color_list[p], label=labels[k]+' \u03B1')

                    # Plotting option for the plot mode OPPOSITE
                    if plot_mode=='OPPOSITE':
                        axs[k].plot(dataset2[0], dataset2[i], color=color_list[p],linestyle=('dashed'), label=labels[k]+' \u03B2')
                        y_mn = min(y_mn_beta)

                    # Plotting option for the plot mode OVERLAP
                    elif plot_mode=='OVERLAP':
                        axs[k].plot(dataset2[0], -dataset2[i], color=color_list[p],linestyle=('dashed'), label=labels[k]+' \u03B2')
                        y_mn = min(y_mn_alpha)

                   
                    y_mx = max(y_mx_alpha)

                    # Fermi level plot
                    y_fermi = np.linspace(y_mn-6, y_mx+6, 2)
                    axs[k].plot(x_fermi, y_fermi, color='blue')

                axs[k].set_xlim([x_mn, x_mx])

                # Plotting option for the plot mode OPPOSITE
                if plot_mode=='OPPOSITE':
                    axs[k].set_ylim([y_mn-5, y_mx+5])

                # Plotting option for the plot mode OVERLAP
                elif plot_mode=='OVERLAP':
                    axs[k].set_ylim([0,y_mx+5])

                axs[k].legend()

                # Zero DOS line plot
                if plot_mode=='OPPOSITE':
                    x_zero = np.linspace(x_mn, x_mx, 2)
                    axs[k].plot(x_zero, y_zero, color='black')

            plt.xlabel('Energy (eV)')
            fig.text(0.06, 0.5, 'DOS (a.u.)', ha='center',
                     va='center', rotation='vertical')

    elif number_of_projections1==1:
        fig=plt.figure()
        for p in range(0, len(dataset_list1)):
            dataset1=dataset_list1[p]
            dataset2=dataset_list2[p]
            plt.plot(dx_fermi_alpha[p], dataset1[1], color=color_list[p], label=labels[p]+' \u03B1')

            # Plotting option for the plot mode OPPOSITE
            if plot_mode=='OPPOSITE':
                plt.plot(dx_fermi_beta[p], dataset2[1], color=color_list[p], linestyle='dashed', label=labels[p]+' \u03B2')
                y_mn=min(y_mn_beta)
 
            # Plotting option for the plot mode OVERLAP               
            elif plot_mode=='OVERLAP':
                plt.plot(dx_fermi_beta[p], -dataset2[1], color=color_list[p],linestyle='dashed', label=labels[p]+' \u03B2')
                y_mn=min(y_mn_alpha)
            

        y_mx=max(y_mx_alpha)


        #fermi_energy plot
        y_fermi=np.linspace(y_mn-6,y_mx+6, 2)
        plt.plot(x_fermi,y_fermi,color='blue')

        #Zero DOS line plot
        if plot_mode=='OPPOSITE':
            x_zero=np.linspace(x_mn,x_mx,2)
            plt.plot(x_zero,y_zero,color='black')

        plt.xlim([x_mn,x_mx])
        plt.ylim([y_mn-4,y_mx+4])
        plt.xlabel('Energy (eV)')
        plt.ylabel('DOS (a.u)')
        plt.legend()



    plt.show()


# Program execution
if file_number == 'SINGLE':
    file = file_list[0]

    # closed shell plotting
    if shell == 'CLOSED':
        parameter_plot = closed_shell_read(file, labels)
        closed_shell_plot(parameter_plot[0], parameter_plot[1],parameter_plot[2], labels)

    # open shell plotting
    elif shell == 'OPEN':
        parameter_plot = open_shell_read(file, labels)
        open_shell_plot(parameter_plot[0], parameter_plot[1],
                        parameter_plot[2], parameter_plot[3], parameter_plot[4], labels)

if file_number == 'MULTIPLE':

    # closed shell plotting
    if shell == 'CLOSED':
        parameter_plot = compare_closed_shell_file_read(file_list, labels)
        compare_closed_shell_plot(parameter_plot[0], parameter_plot[1], parameter_plot[2], labels)

    # open shell plotting
    if shell == 'OPEN':
        parameter_plot = compare_open_shell_file_read(file_list, labels)
        compare_open_shell_plot(parameter_plot[0], parameter_plot[1],
                                parameter_plot[2], parameter_plot[3], parameter_plot[4], labels)


save_opt = input('Do you want to save the image (Y/N): \n')
if save_opt == 'Y':
    name_file = input('Enter the path to save the image:\n')
    plt.savefig(name_file)
