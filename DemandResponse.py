from pyomo.environ import*

#Create model
model=AbstractModel()

#Sets
model.T=Set(initialize=['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12','T13','T14','T15','T16','T17','T18','T19','T20','T21','T22','T23','T24'])  # Add other elements of T
model.L=Set(initialize=['EV','LP','WM','RF','OV','LT'])  # Add other elements of L


#Parameters
model.E=Param(model.T)
model.P=Param(model.L,model.T)
model.K=Param()

#Variables
model.D1=Var(model.L,model.T, within=NonNegativeReals)
model.D2=Var(model.L,model.T, within=NonNegativeReals)
model.DR=Var(model.L,model.T, within=NonNegativeReals)

#Objective Function
def objective_rule(model):
    return sum(model.DR[i,t]*model.E[t] for i in model.L for t in model.T)
model.Emissionfunction=Objective(rule=objective_rule, sense=minimize)

#Constraints
def DemansResponse_rule(model,i, t): # Add time index to the rule
    if i in ["WM", "EV", "OV", "LP"]: 
        return model.DR[i,t] == model.P[i, t]+model.D1[i, t]-model.D2[i, t] 
    if i in ["RF", "LT"]: 
        return model.DR[i,t] == model.P[i, t] 
model.DemandConstraint=Constraint(model.L, model.T, rule=DemansResponse_rule) # Use Constraint for indexed constraints


def UpDemandResponse_rule(model,i, t): # Add time index to the rule
    if i in ["WM", "EV", "OV", "LP"]: 
        return model.D1[i,t] <= model.K*model.P[i, t]
    # Add a condition to handle the case where i is 'RF' or 'LT'
    else:
        return Constraint.Skip # or any other suitable constraint 
model.UpDemandConstraint=Constraint(model.L, model.T, rule=UpDemandResponse_rule)
    

def DownDemandResponse_rule(model,i, t): # Add time index to the rule
    if i in ["WM", "EV", "OV", "LP"]: 
        return model.D2[i,t] <= model.K*model.P[i, t]
    else:
        return Constraint.Skip # or any other suitable constraint
model.DownDemandConstraint=Constraint(model.L, model.T, rule=DownDemandResponse_rule) # Use Constraint for indexed constraints

def ShiftLoadEquality_rule(model,i):
    if i in ["WM", "EV", "OV", "LP"]: 
        return sum(model.D1[i,t] for t in model.T) == sum(model.D2[i,t] for t in model.T) 
    else:
        return Constraint.Skip # or any other suitable constraint
model.EqualityConstraint=Constraint(model.L, rule=ShiftLoadEquality_rule)
   

#Create Instance
data=DataPortal()
data.load(filename="LoadDemand.dat", model=model)
instance=model.create_instance(data)
instance.pprint()

#Solving model
optimizer=SolverFactory("glpk")
optimizer.solve(instance)
instance.display()    
