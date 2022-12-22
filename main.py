import streamlit as st
import pandas as pd
# Specklepy
# The `StreamWrapper` gives you some handy helpers to deal with urls 
# and get authenticated clients and transports.
from specklepy.api.wrapper import StreamWrapper
# The `SpeckleClient` is your entry point for interacting with your Speckle Server's GraphQL API.
# To authenticate the client, you'll need to have downloaded the [Speckle Manager](<https://speckle.guide/#speckle-manager>)
# and added your account.
from specklepy.api.client import SpeckleClient
# Receives an object from a transport given its obj id.
from specklepy.api import operations

# FUNCTIONS⏯

# get category names from commit data
def get_categories_from_commit(commit_data, category_names):
    for member in commit_data.get_member_names():
        if "@" in member:
            category_names.append(member)
    return category_names


# get all parameters from category
def get_parameters_from_category(commit_data, selected_category, output_list):
    category_elements = commit_data[selected_category]
    for element in category_elements:
        parameters = element["parameters"].get_dynamic_member_names()
        for parameter in parameters:
            parameter_name = element["parameters"][parameter]["name"]
            if parameter_name not in output_list:
                output_list.append(parameter_name)
    return output_list

def get_windows_from_curtain_panels(commit_data):
    windows = []
    curtain_panels = commit_data["@Curtain Panels"]
    for cpanel in curtain_panels:
        subelems = cpanel.elements
        if subelems == None: continue
        for element in cpanel.elements:
            if element.category == 'Windows':
                windows.append(element)

    return windows

# gets parameter value from parameter name
def get_parameter_by_name(element, parameter_name, dict):
    parameters = element["parameters"].get_dynamic_member_names()
    for parameter in parameters:
        key = element["parameters"][parameter]["name"]
        if key == parameter_name:
            dict[parameter_name] = element["parameters"][parameter]["value"]
    return dict

#PAGE CONFIG
st.set_page_config(
    page_title="Schedule App",
    page_icon="📚"
)
# CONTAINERS📦
header = st.container()
input = st.container()
data = st.container()

# HEADER
with header:
    st.title("📚 Schedule App")
    st.info(
        "Specklepy exercise for creating the schedules of the future from Revit data."
    )

with input:
    st.subheader("Inputs")
    commit_url = st.text_input(
        "Commit URL",
        "https://speckle.xyz/streams/325ca2fe54/commits/3958a69e12",
    )

# WRAPPER 🌮
# The `StreamWrapper` gives you some handy helpers to deal with urls 
# and get authenticated clients and transports.
wrapper = StreamWrapper(commit_url)
# get an authenticated SpeckleClient if you have a local account for the server
client = wrapper.get_client()
# get an authenticated ServerTransport if you have a local account for the server
transport = wrapper.get_transport()

# COMMIT 🍀
# gets a commit given a stream and the commit id
commit = client.commit.get(wrapper.stream_id, wrapper.commit_id)
# get obj id from commit
obj_id = commit.referencedObject
# receive objects from commit
commit_data = operations.receive(obj_id, transport)


# CATEGORIES
category_names = []
get_categories_from_commit(commit_data, category_names)
# windows = get_windows_from_curtain_panels(commit_data)

# category dropdown
with input:
    selected_category = st.selectbox(
        "Select Category",
        category_names,
    )
# PARAMETERS
# get  parameters from selected category
parameters = []
parameters = sorted(
    get_parameters_from_category(commit_data, selected_category, parameters)
)
# elements from selected category
category_elements = commit_data[selected_category]
# parameter multi-select
with input:
    form = st.form("form")
    with form:
        selected_parameters = st.multiselect(
            "Select parameters",
            parameters,
            key="selected_parameters",
        )
        st.form_submit_button("Create Schedule")

# DATA
with data:
    result_data = []
    for element in category_elements:
        dict = {}
        for s_param in selected_parameters:
            get_parameter_by_name(element, s_param, dict)
        result_data.append(dict)
    # resulting data to DataFrame
    result_DF = pd.DataFrame.from_dict(result_data)
    # Dataframe to CSV
    # Download CSV
    col1, col2 = st.columns([3, 1])
    st.dataframe(result_DF)

