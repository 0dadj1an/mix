from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import argparse
import atexit
import getpass
import ssl
from pickle import FALSE
from time import sleep

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description='Process args for retrieving all the Virtual Machines')
   parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
   args = parser.parse_args()
   return args


def PrintVmInfo(vm, depth=1):
   """
   Print information for a particular virtual machine or recurse into a folder
   or vApp with depth protection
   """
   maxdepth = 10

   # if this is a group it will have children. if it does, recurse into them
   # and then return
   if hasattr(vm, 'childEntity'):
      if depth > maxdepth:
         return
      vmList = vm.childEntity
      for c in vmList:
         PrintVmInfo(c, depth+1)
      return

   # if this is a vApp, it likely contains child VMs
   # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
   if isinstance(vm, vim.VirtualApp):
      vmList = vm.vm
      for c in vmList:
         PrintVmInfo(c, depth + 1)
      return

   summary = vm.summary
   print("Name       : ", summary.config.name)
   print("Path       : ", summary.config.vmPathName)
   print("Guest      : ", summary.config.guestFullName)
   annotation = summary.config.annotation
   if annotation != None and annotation != "":
      print("Annotation : ", annotation)
   print("State      : ", summary.runtime.powerState)
   if summary.guest != None:
      ip = summary.guest.ipAddress
      if ip != None and ip != "":
         print("IP         : ", ip)
   if summary.runtime.question != None:
      print("Question  : ", summary.runtime.question.text)
   print("")


def listVM(si):
     content = si.RetrieveContent()
     for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
         datacenter = child
         vmFolder = datacenter.vmFolder
         vmList = vmFolder.childEntity
         for vm in vmList:
            PrintVmInfo(vm)
     return 0 
 
def powerON(vmlist):
     for vm in vmlist:
         if (vm.name == "checkpoint" or vm.name =="windows"):
             vm.PowerOn()
             print("Virtual Machine(s) have been powered on successfully")       
             
     
def powerOFF(vmlist):
     for vm in vmlist:
         if (vm.name == "checkpoint" or vm.name =="windows"):
             vm.PowerOff()
             print("Virtual Machine(s) have been powered off successfully")


def vmStatus(vmlist):
    for vm in vmlist:
        if (vm.guest.guestState == "running"):
            return True
        else:
            return False
        

def revertToSnapshot(vmlist):
       
    snapshot_name = 'snapshot_name2' # snapshot name
    for vm in vmList:
        if vm.name in vmnames:
            snapshots = vm.snapshot.rootSnapshotList
            for snapshot in snapshots:
                    if snapshot_name == snapshot.name:
                        snap_obj = snapshot.snapshot
                        print ("Reverting snapshot ", snapshot.name)
                        task = [snap_obj.RevertToSnapshot_Task()]
                        WaitForTasks(task, si)
     
    
def main():
   """
   Simple command-line program for listing the virtual machines on a system.
   """

   args = GetArgs()
   if args.password:
      password = args.password
   else:
      password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))

   context = None
   if hasattr(ssl, '_create_unverified_context'):
      context = ssl._create_unverified_context()
   si = SmartConnect(host=args.host,
                     user=args.user,
                     pwd=password,
                     port=int(args.port),
                     sslContext=context)
   if not si:
       print("Could not connect to the specified host using specified "
             "username and password")
       return -1

   atexit.register(Disconnect, si)
   
   
   listVM(si)
   content = si.content
   objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.VirtualMachine],
                                                        True)
   vmList = objView.view
   objView.Destroy()
   #powerON(vmList)
   #vmStatus(vmList)
   ip1 = "1.1.1.1"
   ip2 = "1.1.1.2"
   for vm in vmList:
        adaptermap = vim.vm.customization.AdapterMapping()
        globalip = vim.vm.customization.GlobalIPSettings()
        adaptermap.adapter = vim.vm.customization.IPSettings()
        adaptermap.adapter.ip = vim.vm.customization.FixedIp()
        
            
        
        
        adaptermap.adapter.ip.ipAddress = "1.1.1.1"
        adaptermap.adapter.subnetMask = "255.255.255.0"
        adaptermap.adapter.gateway = "1.1.1.254"  
        
        
        globalip = vim.vm.customization.GlobalIPSettings()
        
        #For Linux . For windows follow
        ident = vim.vm.customization.LinuxPrep(domain="local.local", hostName=vim.vm.customization.FixedName(name="checkpoint"))        
        
        customspec = vim.vm.customization.Specification()
        #For only one adapter
        customspec.identity = ident
        customspec.nicSettingMap = [adaptermap]
        customspec.globalIPSettings = globalip
        
        #Configuring network for a single NIC
        #For multipple NIC configuration contact me.

        print ("Reconfiguring VM Networks . . .")
        
        task = vm.Customize(spec=customspec)
        
        print(adaptermap)
        print (adaptermap.adapter.ip.ipAddress)
        
       
       
       
       
            
           
   

   

# Start program
if __name__ == "__main__":
   main()
