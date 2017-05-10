#!/usr/bin/python3 
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/components')
import random
import time

from sim_components import *


"""
This is a starter pack for a cpu scheduling project. The code / classes provided are to give you a
head start in creating the scheduling simulation. Obviously this is a simulation, so the majority
of the concepts are "simulated". For example, process "burst times" and "IO times" are known
a-priori (not so in real world). Things like memory are abstracted from addressable locations and
page tables to total "blocks" needed.
"""

QUANTUM  = 100 #Time quantun of CPU for Processes in L1 level in Ready queue
QUANTUM1 = 300 #Time quantun of CPU for Processes in L2 level in Ready queue
Required_Memorysize = 512 # memory size of each process for to enter into job_scheduling_queue
EPS=0.0001 #dEclares the EPS value to constant value.

#return empty array
def empty():
    return []

#print process
def print_schedule(process_id, time,mem_required,burst_time,startTime,com_time):
    return "%5d  %9d  %9d  %8d  %10d  %9d"%(process_id, time,mem_required,burst_time,startTime,com_time)

#print event
def print_event(e):
    print("Event: %s   Time: %s" % (e['event'], e['time']))

#remove from events 
def erase(proc_events, events):
    for event in proc_events:
        if(event['time'] in events):  del events[event['time']]
    return empty()

#get format string to print 
def get_params(arr,sp):
    n=len(arr[0])
    s='"'
    p=arr[0]
    for i in range(n):
        if i:s+=sp
        s+='%'+str(p[i])+'d'
    s+='\\n"%('
    p=arr[1]
    for i in range(n):
        if i:s+=","
        s+=str(p[i])
    s+=")"
    return eval(s)  
	
#==============Class: MLFQ==================
class MLFQ(object):
    """Multi-Level Feedback Queue

    - Some general requirements for a MLFQ:
        - Each queue needs its own scheduling algorithm (typically Fcfs).
        - The method used to determine when to upgrade a process to a higher-priority queue.
        - The method used to determine when to demote a process to a lower-priority queue.
        - The method used to determine which queue a process will enter when that process needs
        service.

    - Rule 1: If Priority(A) > Priority(B), A runs (B doesn't).
    - Rule 2: If Priority(A) = Priority(B), A & B run in RR.
    - Rule 3: When a job enters the system, it is placed at the highest priority (the topmost
              queue).
    - Rule 4: Once a job uses up its time allotment at a given level (regardless of how many times
              it has given up the CPU), its priority is reduced (i.e., it moves down one queue).
    - Rule 5: After some time period S, move all the jobs in the system to the topmost queue.

    - **Attributes**:
        - self.num_levels
        - self.queues
    """
    def __init__(self, num_levels=2):
        self.num_levels = num_levels
        self.queues=empty()
        for i in range(self.num_levels): self.queues.append(Fifo())

    def new(self, process):
        """This method admits a new process into the system.
        - **Args:**
            - process
        - **Returns:**
            - None
        """
        q=self.queues[process.priority]
        q.add(process)

    def nextProcess(self):
        #return  process with hight else low priority
        if not self.queues[1].empty():  return self.queues[1].remove() 

        if not self.queues[0].empty():  return self.queues[0].remove()
        return None

# === Class: Scheduler===
class Scheduler(object):
    """
    New:        In this status, the Process is just made or created.
    Running:    In the Running status, the Process is being executed.
    Waiting:    The process waits for an event to happen for example an input from the keyboard.
    Ready:      In this status the Process is waiting for execution in the CPU.
    Terminated: In this status the Process has finished its job and is ended.
    """
    def __init__(self, *args, **kwargs):
        self.clock = Clock()
        self.memory = Memory()                  
        self.cpu = Cpu()
        self.accounting = SystemAccounting()
        #selecting or taking semahore one in the range of 5.
        self.semaphore = [Semaphore(1) for _ in range (5)]
		#This Job_Scheduling queue will follow the FIFO order when processes enter into it.
        self.job_scheduling_queue = Fifo()
        #this gives list of jobs into events.
        self.events = kwargs['jobs']
		#process list from MLFQ queue.
        self.ready = MLFQ() 
		#finished process's list will be present in Finished Queue.
        self.finished=empty() 
		#Time quantun of CPU for both L1 and L2 in ready queue.
        self.quantum = [QUANTUM1, QUANTUM]
		#directory 
        self.io_queue = {}

    def new_process(self,job_info):
        """New process entering system gets placed on the 'job_scheduling_queue'.
        - **Args**:
            - job_info (dict): Contains new job information.
        - **Returns**:
            - None
        """
        # This loop will takes the process which has the memory size less than Required_memorysize only.
        if int(job_info['mem_required']) > Required_Memorysize:
           print ("This job exceeds the system's main memory capacity.")
           return
     
        self.job_scheduling_queue.add(Process(**job_info))
        self.schedulejob()

         #This will add the jobs or process into schedulejob queue.
        

    def ioperformance(self,info):
        #gives the burst_time value of the i/o process
        ioBurstTime=int(info['ioBurstTime'])
        cur_proc = self.cpu.running_process
        #This will give the complete time for each process to run on CPU. 
        completeTime = self.clock.clock + ioBurstTime
        if cur_proc == None: pass

        cur_proc.iostart = self.clock.clock
        #calculates the Bursttime of the process.
        cur_proc.ioburst =  ioBurstTime
        #it removes the processes.
        self.cpu.remove_process()
        cur_proc.events=erase(cur_proc.events,self.events)
        self.Newevent(cur_proc, completeTime, 'C')
        if str(completeTime) not in self.io_queue: self.io_queue[str(completeTime)]=empty()
        self.io_queue[str(completeTime)].append(cur_proc)
        self.schedulingprocess()

    # This Function will acquires the semahore when the particular input comes from file.
    def acquiringsemaphore(self,info):
        runningProcess = self.cpu.running_process
        if  not self.semaphore[int(info['semaphore'])].acquire(runningProcess): #need to wait
            erase(runningProcess.events,self.events)
            self.cpu.remove_process()
            self.schedulingprocess()

    #This Function will terminate the semaphore when the particular input comes from file.
    def terminate_semaphore(self, info):
        #It will deallocate the current running pocess on cpu
        self.memory.deallocate(self.cpu.running_process.process_id)
        self.cpu.running_process.com_time = self.cpu.system_clock.current_time()
        self.finished.append(self.cpu.running_process)
        erase(self.cpu.running_process.events,self.events)
        self.cpu.remove_process()
        self.schedulejob()

    #This Function will Release the semaphore when the particular input comes from the file.
    def releasesemaphore(self,info):
       # It will displays the current process in CPU.
        cur_proc = self.cpu.running_process
        process = self.semaphore[int(info['semaphore'])].release()
        if process:  
            process.priority = 1
            self.ready.new(process)  
            self.schedulingprocess()

    
    #This Function will expires the semaphore when the particular input comes from the file.
    def semaphore_expire(self, info):
        runningProcess = self.cpu.running_process
        runningProcess.priority = 0 
        runningProcess.quantum = QUANTUM
        erase(runningProcess.events,self.events)
        self.cpu.remove_process()
        self.ready.new(runningProcess) 
        self.schedulingprocess()

    #This Function defines the i/o completion
    def completionof_io(self, info):
        #This Loop will checks till complete all cpu_process which are in i/o queue.
        for cpu_process in self.io_queue[info['time']]: 
             #sets the priority of the  cpu process to 1.
            cpu_process.priority = 1
            cpu_process.quantum = QUANTUM
            self.ready.new(cpu_process)
        self.schedulingprocess()

#This Function will schedule all jobs into a job_scheduling_queue after checking the memory requirement. 
    def schedulejob(self):
        systemtime = self.clock.current_time()
        process = self.job_scheduling_queue.first()

        while process and self.memory.fits(process['mem_required']):
            #this allocates memory to the process in ready queue after checks memory capacity. 
            self.memory.allocate(process)
            process.inScheduleTime = self.clock.current_time()
            self.job_scheduling_queue.remove()
             #sets process priority to 1.
            process.priority = 1
            self.ready.new(process)
            process = self.job_scheduling_queue.first()
        #checks if cpu is not busy then allocates process to cpu.
        if not self.cpu.busy(): self.schedulingprocess()

#This function will defines scheduling process and checks if cpu is busy or not. 
    def schedulingprocess(self):
        if self.cpu.busy():
            a = self.cpu.running_process.priority  
            if a == 0 and not self.ready.queues[1].empty():   
                cur_proc = self.cpu.running_process   
                self.ready.new(cur_proc)
                self.cpu.remove_process()
                erase(cur_proc.events,self.events)
            else: return

        process = self.ready.nextProcess()

        if not process:  return
        if not process.startTime:  process.startTime = self.clock.clock  
         #gives the termination time by burst time of process and clock time. 
        terminate_time = self.clock.clock + int(process.burst_time)
        process.quantum = self.quantum[process.priority]

        self.Newevent(process, self.clock.clock + process.burstLeft, 'T')
        self.Newevent(process, self.clock.clock + process.quantum, 'E')

        self.cpu.run_process(process)
   
   #It defines new event.
    def Newevent(self, process, time, event):
        time=str(time)
        if event == 'E' and time in self.events: 
            for e in self.events[time]:
                if e['event']=='T': return
        new_event={'time':time, 'event': event}
        process.events.append(new_event)

        if time not in self.events: self.events[time] = empty()
        self.events[time].append(new_event)
        
# === Class: Simulator===
class Simulator(object):
   
   
    def __init__(self, **kwargs):

        # This will continue only when the input file is present else raise an exception.
        if 'input_file' in kwargs:  self.input_file = kwargs['input_file']
        else: raise Exception("Input file needed for simulator")
        #initialsing clock to zero.
        self.start_clock = 0

        #writing  an output into a file
        if 'output_file' in kwargs:  sys.stdout = open(kwargs['output_file'],"w")

        # Read jobs in a priority from input file.
        self.jobs_dict = load_process_file(self.input_file,return_type="Dict")

        # create system clock and do a hard reset it to make sure
        # its a fresh instance. 
        self.system_clock = Clock()
        self.system_clock.hard_reset(self.start_clock)

        # Initialize all the components of the system.
        
        self.memory = Memory()
        self.cpu = Cpu()
        self.accounting = SystemAccounting()

        localEvents = {}
        self.scheduler = Scheduler(jobs = localEvents)
        
        # This dictionary holds key->value pairs where the key is the "event" from the input
        # file, and the value = the "function" to be called.
        # A = new process enters system             -> calls scheduler.new_process
        # D = Display res of simulator           -> calls get_status
        # I = Process currently on cpu performs I/O -> calls scheduler.ioperformance 
        # S = Semaphore signal (release)            -> calls scheduler.acquiringsemaphore
        # W = Semaphore wait (acquire)              -> calls scheduler.releasesemaphore
        self.event_dispatcher = {
            'A': self.scheduler.new_process,
            'D': self.get_status,
            'I': self.scheduler.ioperformance,
            'W': self.scheduler.acquiringsemaphore,
            'S': self.scheduler.releasesemaphore,
            'T': self.scheduler.terminate_semaphore,
            'E': self.scheduler.semaphore_expire,
            'C': self.scheduler.completionof_io
        }

        # While there are still jobs to be processed
        while len(self.jobs_dict) > 0 or len(localEvents) > 0:
            key = str(self.system_clock.current_time())
            if key in localEvents:
                for event in localEvents[key]:
                    event_data = event
                    event_type = event_data['event']
                    print_event(event_data)
                    self.event_dispatcher[event_type](event_data)
  
            # If current time is a key in dictionary, run that event.
            if key in self.jobs_dict.keys():
                event_data = self.jobs_dict[key]
                del self.jobs_dict[key]
                
                print_event(event_data)
                dispatcher=self.event_dispatcher[event_data['event']]
                res = dispatcher(event_data)
                if res: print(res)

            if self.cpu.running_process:
                self.cpu.running_process.burstLeft = self.cpu.running_process.burstLeft - 1
                self.cpu.running_process.quantum = self.cpu.running_process.quantum - 1
            #This will increase the system clock by 1 every time. 
            self.system_clock += 1

        print("\nThe contents of the FINAL FINISHED LIST\n---------------------------------------\n\n" \
                "Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time\n"\
                "-----  ---------  ---------  --------  ----------  ---------\n")
        #Initialsing all values to zero initially.
        total_around,total_wait,total_schedule,num_finished = 0, 0, 0, 0
        for finished in self.scheduler.finished:
            process_id=int(finished.process_id)
            time=int(finished.time)
            mem_required=int(finished.mem_required)
            burst_time=int(finished.burst_time)
            startTime=int(finished.startTime)
            com_time=finished.com_time
            
            print(print_schedule(process_id, time,mem_required,burst_time,startTime,com_time))
            #Gives the total aroud time.
            total_around = total_around + (com_time - time)
            #gives the total wait time of the process.
            total_wait = total_wait + (int(finished.inScheduleTime) - time )
            num_finished = num_finished + 1

        print("\n")
        #prints turnaround time,total wait time and number of block in main memory.
        print("The Average Turnaround Time for the simulation was %.3f units.\n" % (total_around / num_finished-EPS))
        print("The Average Job Scheduling Wait Time for the simulation was %.3f units.\n" % (total_wait / num_finished-EPS))
        print("There are %d blocks of main memory available in the system.\n" % (self.memory.available()))
        sys.stdout.close()

    #This Function will give the table of the processes.
    def get_process_table(self, table):
        if table.empty():  return "The Job Scheduling Queue is empty.\n"
        else:
            res = "Job #  Arr. Time  Mem. Req.  Run Time\n-----  ---------  ---------  --------\n\n"
            for p in table: res = res + get_params([[5,10,10,9],[p.process_id,p.time,p.mem_required,p.burst_time]]," ")
            return res
     #This Function will get the semaphore and displays the semaphores
    def get_semaphore(self, n):
        values = ["ZERO", "ONE", "TWO", "THREE", "FOUR"]
        upvalue = "The contents of SEMAPHORE %s"%values[n]
        outval = upvalue+"\n"+("-"*len(upvalue))+"\n\n"
        outval = outval + "The value of semaphore %d is %d.\n\n"%(n, self.scheduler.semaphore[n].current)
        if self.scheduler.semaphore[n].acquired_dict.empty(): return  outval + ("The wait queue for semaphore %d is empty.\n\n\n"%n)
        for process in self.scheduler.semaphore[n].acquired_dict.Q: outval = outval + str(process.process_id) + "\n"
        return  outval + "\n\n"
    #This Function will give the status of simulator, first level and second level and i/o queues.
    def get_status(self,info):
        res = "\n************************************************************\n\n"
        res = res + "The status of the simulator at time %s.\n\n"%info['time']
        res = res + "The contents of the JOB SCHEDULING QUEUE\n----------------------------------------\n\n"
        res = res + self.get_process_table(self.scheduler.job_scheduling_queue)   
        res = res + "\n\nThe contents of the FIRST LEVEL READY QUEUE\n-------------------------------------------\n\n"

        if self.scheduler.ready.queues[1].empty(): res = res + "The First Level Ready Queue is empty.\n"
        else: res = res + self.get_process_table(self.scheduler.ready.queues[1])
        res = res + "\n\nThe contents of the SECOND LEVEL READY QUEUE\n--------------------------------------------\n\n"
        
        if self.scheduler.ready.queues[0].empty(): res += "The Second Level Ready Queue is empty.\n"
        else: res = res + self.get_process_table(self.scheduler.ready.queues[0])
        res = res + "\n\nThe contents of the I/O WAIT QUEUE\n----------------------------------\n\n"
        
        jobs = empty()
        for time in self.scheduler.io_queue:
            if self.system_clock.current_time() <int(time):
                for job in self.scheduler.io_queue[time]:
                    jobs.append([job.iostart+job.ioburst,int(job.process_id), int(job.time), int(job.mem_required), int(job.burst_time),  job.iostart,  job.ioburst])
        jobs.sort()
        if not jobs: res = res + "The I/O Wait Queue is empty.\n"
        else:
            res = res +  "Job #  Arr. Time  Mem. Req.  Run Time  IO Start Time  IO Burst  Comp. Time\n"   \
                "-----  ---------  ---------  --------  -------------  --------  ----------\n\n"
            for job in jobs:  res = res + get_params([[5,9,9,8,13,8,10],[job[1], job[2], job[3],job[4],job[5],job[6],job[0]]],"  ")
        res =res + "\n\n"

        for i in range(5):  res = res + self.get_semaphore(i)
        cur_proc = self.cpu.running_process
        res = res + "The CPU  Start Time  CPU burst time left\n-------  ----------  -------------------\n\n"

        if cur_proc: res =res + get_params([[7,10,19],[cur_proc.process_id,cur_proc.startTime,cur_proc.burstLeft]],"  ")
        else: res = res + "The CPU is idle.\n"

        res = res +  "\n\nThe contents of the FINISHED LIST\n---------------------------------\n\n" \
                "Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time\n" \
                "-----  ---------  ---------  --------  ----------  ---------\n\n"

        for finished in self.scheduler.finished:    res = res + print_schedule(int(finished.process_id),int(finished.time),
                                                                         int(finished.mem_required), int(finished.burst_time),
                                                                         int(finished.startTime),finished.com_time)+"\n"
        res = res + "\n\nThere are %d blocks of main memory available in the system.\n"%(self.memory.available())
        return res



# Test Functions
def run_tests():
    print("############################################################")
    print("Running ALL tests .....\n")

    test_process_class()
    test_class_clock()
    test_cpu_class()
    test_memory_class()
    test_semaphore_class()



if __name__ == '__main__':
    #taking the input from jobs_in_c.txt
    file_name = os.path.dirname(os.path.realpath(__file__))+'/input_data/jobs_in_c.txt'
    #printing output into a file named jobs_out_c.txt
    S = Simulator(input_file=file_name,output_file="jobs_out_c.txt")
    
