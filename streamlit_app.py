layer = pdk.Layer(
    "ColumnLayer",
    data=df,
    get_position='[lon, lat]',
    get_elevation='elevation',
    radius=12000,
    get_fill_color="""
        [
            Temperature < 10 ? 0 :
            Temperature < 25 ? 255 :
            255,

            Temperature < 10 ? 120 :
            Temperature < 25 ? 200 :
            80,

            Temperature < 10 ? 255 :
            Temperature < 25 ? 0 :
            0,

            180
        ]
    """,
    pickable=True,
    auto_highlight=True,
)

