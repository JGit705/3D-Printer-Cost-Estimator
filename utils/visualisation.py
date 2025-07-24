import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_cost_pie(material_cost, energy_cost, total_cost):
    """
    Display a minimalist, beige-toned pie chart of cost breakdown in Streamlit.
    """
    markup = total_cost - material_cost - energy_cost
    labels = ['Material', 'Energy', 'Markup']
    sizes = [material_cost, energy_cost, markup]
    
    # Beige Monochrome Color Palette
    colors = ['#A68A64', '#CBB89D', '#E8DED1']  # earthy beige, light beige, very light beige

    fig, ax = plt.subplots(figsize=(5, 5), facecolor='none')
    wedges, _, autotexts = ax.pie(
        sizes,
        labels=None,  # No labels on chart
        autopct='%1.0f%%',
        startangle=140,
        colors=colors,
        textprops={'color': 'white', 'fontsize': 18, 'fontfamily': 'DejaVu Sans'},
        wedgeprops={'linewidth': 0}
    )

    # Remove all spines and ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('equal')
    fig.patch.set_alpha(0.0)

    # Add minimalist legend below chart
    legend_patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in range(3)]
    plt.subplots_adjust(bottom=0.25)
    ax.legend(
        handles=legend_patches,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
        frameon=False,
        fontsize=16,
        labelcolor='white'  
    )

    st.pyplot(fig)

# Placeholder for STL 3D preview (to be implemented)
def stl_preview_placeholder():
    st.info("3D STL preview coming soon!")
