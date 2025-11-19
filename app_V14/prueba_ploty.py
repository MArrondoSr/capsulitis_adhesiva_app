import plotly.graph_objects as go
fig = go.Figure(data=[go.Pie(labels=["A","B"], values=[10,90])])
fig.write_image("test.png")
