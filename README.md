# Django Master CASA

A Django web application for [describe your project purpose].

## Features

##Glossary
Acronyms and abbreviations
Acronym / abbreviation	Description
AGL	Above ground level
ALARP	As low as reasonably practicable
ATSB	Australian Transport Safety Bureau
ATC	Air traffic control
BVLOS	Beyond visual line of sight
CAA	Civil Aviation Act 1988 (the Act)
CASA	Civil Aviation Safety Authority
CASR	Civil Aviation Safety Regulations 1998
CRP	Chief remote pilot
EVLOS	Extended visual line of sight
HLS	Helicopter landing site
IAW	In accordance with
JSA	Job safety assessment
MOS	Manual of Standards
MC	Maintenance controller
NM	Nautical miles
NOTAM	Notice to airmen
OC	Operational crew member
RePL	Remote pilot licence
ReOC	Remotely piloted aircraft operator’s certificate 
RP	Remote pilot (or UAV controller)
RPA	Remotely piloted aircraft (same meaning as UAV) 
RPAS	Remotely piloted aircraft system (same meaning as UAS)
SMS	Safety management system
SOC	Standard operating conditions – reference reg 101.238 CASR (1998)
SOP	Standard operating procedures
UOC	Unmanned aerial vehicle operator’s certificate
VLOS	Visual line of sight
VMC	Visual meteorological conditions


- [Add your main features]

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/djorigin/Django_master_CASA.git
   cd Django_master_CASA
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start development server:
   ```bash
   python manage.py runserver
   ```

## Development

- **Current branch**: `feature/client-profile`
- **Main branch**: `master`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

[Add your license information]
