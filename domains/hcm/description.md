# HCM — Human Capital Management

A Human Capital Management system maintains employee records, org structure, leave requests,
and payroll inputs so HR and managers handle workforce changes with consistent approvals.

## Concepts

- **Employee** — a person employed by the organisation with a contract and personnel record.
- **Department** — an organisational unit that groups employees under a common function and budget.
- **Position** — a defined job within the org structure that an employee is appointed to.
- **Payroll** — the periodic run that computes and pays employee compensation from approved inputs.
- **LeaveRequest** — an employee's request for time off, routed through approval and into payroll.
- **Appraisal** — a periodic evaluation of an employee's performance against objectives.

## Taxonomy

- Employee is a kind of Person.
- Department is a kind of OrganisationalUnit.
- Position is a kind of JobDefinition.
- LeaveRequest is a kind of WorkforceRequest.

## Attributes

- Employee: employeeNumber (string), fullName (string), hireDate (date)
- Department: departmentName (string), costCenter (string)
- Position: positionTitle (string), grade (string)
- Payroll: payPeriod (string), grossAmount (decimal), runDate (date)
- LeaveRequest: leaveType (string), startDate (date), endDate (date), leaveRequestStatus (string)
- Appraisal: reviewPeriod (string), rating (string), reviewedAt (dateTime)

## Relationships

- Employee belongsToDepartment Department (many-to-one)
- Employee holdsPosition Position (many-to-one)
- Payroll compensatesEmployee Employee (many-to-one)
- LeaveRequest submittedByEmployee Employee (many-to-one)
- Appraisal evaluatesEmployee Employee (many-to-one)

## Lifecycle

- LeaveRequest: submitted → approved | rejected → reflected

## Roles

- **EmployeeRole** (bearer: person) — maintains own record, submits leave requests, views payslips; permissions: LeaveRequest:read, LeaveRequest:write, Employee:read
- **ManagerRole** (bearer: person) — approves or rejects leave requests and conducts appraisals for direct reports; permissions: LeaveRequest:read, LeaveRequest:write, Appraisal:read, Appraisal:write, Employee:read
- **HRAdministratorRole** (bearer: person) — onboards employees, maintains org structure, and runs payroll; permissions: Employee:read, Employee:write, Department:read, Department:write, Position:read, Position:write, Payroll:read, Payroll:write

## Primary workflow

Onboard employee → assign position → submit leave → approve → reflect in payroll
