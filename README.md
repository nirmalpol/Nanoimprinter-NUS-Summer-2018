# Nanoimprinter-NUS-Summer-2018

This respository contains the improvements, changes, additions and tests performed on the Nanoimprinting Lithography device prototype (nanoimprinter) for the National University of Singapore from the duration of May 21, 2018 to July 27, 2018. The nanoimprinter is designed to replicate a mold containing nanochannels onto a new polymer through the use of heat and pressure. The polymer is placed inside the nanoimprinter and the mold is then placed on top of it after which it will be heated and pressurized. The temperatures can rise up to approximately 150°C and pressurize to a maximum value of 35 bar.
  
           
   ![image](https://user-images.githubusercontent.com/33207203/46577079-00835e00-c9ab-11e8-9794-8ff65425776d.png)

The "Nanoimprinter Code July 19, 2018" contains the UI code, pressure system code(ADC, DAC), and the temperature system code (Thermocouples, Heating elements). The description of each programming file and comments are mentioned in the the file in great detail.
  
The ADC and DAC are industrial models that are connected appropriately based on your respective system and the data sheets provided. As a result, there were no examples on how to connect the electrical components other than reading the data sheets. However, for our project, the goal was to be able to accurately control pressure based on the input and output of the pressure regulator. So the following connections present in the diagram were required for operation:
  
  ![circuitdiagrams-1](https://user-images.githubusercontent.com/33207203/46577015-b4371e80-c9a8-11e8-9403-69d1e299dd01.jpg)

