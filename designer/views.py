# designer/views.py
from django.shortcuts import render
from .forms import DesignForm
from .models import AbayaDesign
from .utils import generate_abaya_design


def index(request):
    return render(request, "messenger.html")


def home(request):
    """
    Render the home page where users can input their design preferences.
    If the form is submitted, process the input, generate a design, and redirect to the result page.
    """
    if request.method == 'POST':
        form = DesignForm(request.POST)
        if form.is_valid():
            design = form.save(commit=False)
            # Integrate AI Model to generate the design
            design_image_path = generate_abaya_design(form.cleaned_data)
            design.design_image = design_image_path
            design.save()
            return render(request, 'result.html', {'design': design})
    else:
        form = DesignForm()
    return render(request, 'messenger.html', {'form': form})
